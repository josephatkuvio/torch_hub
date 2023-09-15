using Sparc.Blossom.Data;
using Torch.Web.Institutions;

namespace Torch.Web.Workflows;

public partial class Workflow : Entity<int>
{
    public Workflow(int institutionId, string name, string description)
    {
        InstitutionId = institutionId;
        Name = name;
        Description = description;
        CreatedDate = DateTime.UtcNow;
    }

    public Workflow(Institution institution, string name, string description) : this(institution.Id, name, description)
    {
        Institution = institution;
    }

    public int InstitutionId { get; private set; }
    public string Name { get; private set; }
    public string? Description { get; private set; }
    public DateTime CreatedDate { get; private set; }
    public DateTime? DeletedDate { get; private set; }
    public Institution Institution { get; private set; } = null!;
    public List<TorchTask> Tasks { get; private set; } = new();
    public List<WorkflowUser> Users { get; private set; } = new();
    public List<Connection> Connections { get; private set; } = new();
    internal Connection? InputConnection => Connections.FirstOrDefault(x => x.Direction == "Input");
    internal Connection? OutputConnection => Connections.FirstOrDefault(x => x.Direction == "Output");

    public void Delete() => DeletedDate = DateTime.UtcNow;
    public void AddTask(string funcName, string name, Dictionary<string, string>? parameters)
    {
        var newTask = new TorchTask(Id, funcName, name, parameters);
        var maxSortOrder = Tasks.Where(x => x.DeletedDate == null).Max(x => x.SortOrder);
        newTask.SetSortOrder((maxSortOrder ?? 0) + 1);
        Tasks.Add(newTask);
    }

    public void DeleteTask(TorchTask task)
    {
        var existingTask = Tasks.FirstOrDefault(x => x.Id == task.Id);
        if (existingTask == null)
            return;

        Tasks.Remove(existingTask);
        UpdateTaskSortOrders();
    }

    internal void UpdateTaskSortOrders()
    {
        var order = 1;
        foreach (var task in Tasks.OrderBy(x => x.SortOrder == null ? 1000 : (x.TemporarySortOrder ?? x.SortOrder)))
        {
            task.SetSortOrder(order);
            order++;
        }
    }
}

