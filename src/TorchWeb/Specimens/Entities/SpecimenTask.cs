using Torch.Web.Workflows;

namespace Torch.Web.Collections;

public class SpecimenTask : TorchTask
{
    public SpecimenTask(int specimenId, string funcName, string name, int sortOrder)
        : base(funcName, name, sortOrder)
    {
        SpecimenId = specimenId;
    }

    public SpecimenTask(int specimenId, TorchTask baseTask)
    : this(specimenId, baseTask.FuncName, baseTask.Name, baseTask.SortOrder)
    {
    }

    public int SpecimenId { get; private set; }
    public string? BatchId { get; private set; }
    public DateTime? StartDate { get; private set; }
    public DateTime? EndDate { get; private set; }
    public string? RunState { get; private set; }
    public string? RunMessage { get; private set; }
    public Specimen Specimen { get; private set; } = null!;
}