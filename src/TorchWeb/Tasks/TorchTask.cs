namespace Torch.Web.Workflows;

public class TorchTask
{
    public TorchTask(int workflowId, string funcName, string name, Dictionary<string, string>? parameters = null)
    {
        WorkflowId = workflowId;
        FuncName = funcName;
        Name = name;
        Parameters = parameters ?? new();
        LastUpdatedDate = DateTime.UtcNow;
    }

    public int Id { get; private set; }
    public int WorkflowId { get; private set; }
    public Workflow Workflow { get; private set; } = null!;
    public string Name { get; private set; }
    public string FuncName { get; private set; }
    public int? SortOrder { get; private set; }
    public string? Description { get; private set; }
    public DateTime LastUpdatedDate { get; private set; }
    public DateTime? DeletedDate { get; private set; }
    public Dictionary<string, string> Parameters { get; private set; }
    internal decimal? TemporarySortOrder { get; private set; }

    public void Delete() => DeletedDate = DateTime.UtcNow;
    public void SetSortOrder(int sortOrder)
    {
        if (SortOrder != sortOrder)
        {
            SortOrder = sortOrder;
            LastUpdatedDate = DateTime.UtcNow;
        }
    }

    public void SetSortOrder(bool moveUp)
    {
        TemporarySortOrder = SortOrder + (moveUp ? -1.5m : 1.5m);
    }
}