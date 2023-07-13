namespace Torch.Web.Collections
{
    public class SpecimenTask
    {
        public SpecimenTask(int specimenId, string funcName, string name, int sortOrder)
        {
            SpecimenId = specimenId;
            FuncName = funcName;
            Name = name;
            SortOrder = sortOrder;
        }

        public int Id { get; private set; }
        public int SpecimenId { get; private set; }
        public string FuncName { get; private set; }
        public string Name { get; private set; }
        public int SortOrder { get; private set; }
        public string? Description { get; private set; }
        public Specimen Specimen { get; private set; } = null!;
        public List<SpecimenTaskParameter> Parameters { get; private set; } = new();
    }
}