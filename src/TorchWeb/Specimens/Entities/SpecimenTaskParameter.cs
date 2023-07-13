using Torch.Web.Workflows;

namespace Torch.Web.Collections;

public class SpecimenTaskParameter : TorchParameter
{
    public SpecimenTaskParameter(int specimenTaskId, string name, string value)
        : base(name, value)
    {
        SpecimenTaskId = specimenTaskId;
    }

    public int SpecimenTaskId { get; private set; }
    public SpecimenTask Task { get; private set; } = null!;
}