using Torch.Web.Workflows;

namespace Torch.Web.Collections;

public class SpecimenTask
{
    public SpecimenTask(int taskId, int specimenId)
    {
        TaskId = taskId;
        SpecimenId = specimenId;
        StartDate = DateTime.UtcNow;
    }

    public int SpecimenId { get; private set; }
    public int TaskId { get; private set; }
    public DateTime StartDate { get; private set; }
    public DateTime? EndDate { get; private set; }
    public string? RunState { get; private set; }
    public string? RunMessage { get; private set; }
    public Specimen Specimen { get; private set; } = null!;
    public TorchTask Task { get; private set; } = null!;
}