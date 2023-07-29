using Sparc.Blossom.Data;
using Torch.Web.Collections;
using Torch.Web.Institutions;

namespace Torch.Web.Workflows;

public class Workflow : Entity<int>
{
    public Workflow(int institutionId, string name, string description)
    {
        InstitutionId = institutionId;
        Name = name;
        Description = description;
        CreateDate = DateTime.UtcNow;
    }

    public int InstitutionId { get; private set; }
    public string Name { get; private set; }
    public string? Description { get; private set; }
    public DateTime CreateDate { get; private set; }
    public DateTime? DeletedDate { get; private set; }
    public Institution Institution { get; private set; } = null!;
    public List<TorchTask> Tasks { get; private set; } = new();
    public List<Specimen> Specimens { get; private set; } = new();

    public void Delete() => DeletedDate = DateTime.UtcNow;
    public void AddTask(TorchTask task) => Tasks.Add(task);
}

