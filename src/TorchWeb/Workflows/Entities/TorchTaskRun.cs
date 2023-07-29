using Torch.Web.Collections;

namespace Torch.Web.Workflows;

public class TorchTaskRun
{
    public int Id { get; set; }
    public int TaskId { get; set; }
    public int SpecimenId { get; set; }
    public string Parameters { get; set; }
    public DateTime StartDate { get; set; }
    public DateTime? EndDate { get; set; }
    public string? Status { get; set; }
    public string? Result { get; set; }
    public TorchTask Task { get; set; } = null!;
    public Specimen Specimen { get; set; } = null!;
}

