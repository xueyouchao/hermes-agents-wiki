package workflow

import (
    "time"
    "go.temporal.io/sdk/workflow"
    "polymarket-arbitrage/internal/domain/aggregate"
)

type OpportunityExecutionInput struct {
    Opportunity aggregate.Opportunity
    Legs        []aggregate.Leg
}

type OpportunityExecutionResult struct {
    TradeID string
    Status  string
    PnL     float64
}

type OpportunityActivities interface {
    CheckRisk(ctx context.Context, opp aggregate.Opportunity, legs []aggregate.Leg) error
    PlaceOrder(ctx context.Context, leg aggregate.Leg) (OrderResult, error)
    ReverseOrder(ctx context.Context, leg OrderResult) error
    ConfirmSettlement(ctx context.Context, trade aggregate.Trade) error
    SaveTrade(ctx context.Context, trade aggregate.Trade) error
}

type OrderResult struct {
    ExternalID string
    Filled     bool
    Price      float64
    Timestamp  time.Time
}

func OpportunityExecution(ctx workflow.Context, input OpportunityExecutionInput) (OpportunityExecutionResult, error) {
    ao := workflow.ActivityOptions{
        StartToCloseTimeout: 5 * time.Second,
        RetryPolicy: &temporal.RetryPolicy{
            InitialInterval:    500 * time.Millisecond,
            MaximumInterval:    2 * time.Second,
            MaximumAttempts:    3,
            NonRetryableErrorTypes: []string{"RiskError"},
        },
    }
    ctx = workflow.WithActivityOptions(ctx, ao)

    // Risk check
    var activities OpportunityActivities
    if err := workflow.ExecuteActivity(ctx, activities.CheckRisk, input.Opportunity, input.Legs).Get(ctx, nil); err != nil {
        return OpportunityExecutionResult{Status: "RISK_REJECTED"}, nil
    }

    // Place orders with compensation (SAGA)
    results := make([]OrderResult, len(input.Legs))
    for i, leg := range input.Legs {
        var res OrderResult
        if err := workflow.ExecuteActivity(ctx, activities.PlaceOrder, leg).Get(ctx, &res); err != nil {
            // Compensate: reverse all prior legs
            for j := i - 1; j >= 0; j-- {
                _ = workflow.ExecuteActivity(ctx, activities.ReverseOrder, results[j]).Get(ctx, nil)
            }
            return OpportunityExecutionResult{Status: "EXECUTION_FAILED"}, err
        }
        results[i] = res
    }

    // Build trade aggregate
    trade := aggregate.NewTrade(
        uuid.New().String(),
        input.Opportunity.ID,
        input.Legs,
    )
    trade.State = aggregate.TradeExecuted
    trade.CreatedAt = workflow.Now(ctx)

    // Confirm settlement (durable polling)
    settleCtx := workflow.WithActivityOptions(ctx, workflow.ActivityOptions{
        StartToCloseTimeout: 60 * time.Second,
    })
    if err := workflow.ExecuteActivity(settleCtx, activities.ConfirmSettlement, *trade).Get(settleCtx, nil); err != nil {
        // Partial compensation
        for _, r := range results {
            _ = workflow.ExecuteActivity(settleCtx, activities.ReverseOrder, r).Get(settleCtx, nil)
        }
        return OpportunityExecutionResult{Status: "SETTLEMENT_FAILED"}, err
    }

    trade.State = aggregate.TradeSettled
    now := workflow.Now(ctx)
    trade.SettledAt = &now

    // Persist
    _ = workflow.ExecuteActivity(ctx, activities.SaveTrade, *trade).Get(ctx, nil)

    return OpportunityExecutionResult{
        TradeID: trade.ID,
        Status:  "SETTLED",
        PnL:     0, // computed from filled prices in real system
    }, nil
}
