namespace Torch.Web.Collections
{
    public class SpecimenTaskParameter
    {
        public SpecimenTaskParameter(int specimenTaskId, string name, string value)
        {
            SpecimenTaskId = specimenTaskId;
            Name = name;
            Value = value;
        }

        public int Id { get; private set; }
        public int SpecimenTaskId { get; private set; }
        public string Name { get; private set; }
        public string Value { get; private set; }
        public SpecimenTask Task { get; private set; } = null!;
    }
}