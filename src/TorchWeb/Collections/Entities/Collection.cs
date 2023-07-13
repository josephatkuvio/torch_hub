using Sparc.Blossom.Data;

namespace Torch.Web.Collections;

public class Collection : Entity<int>
{
    public Collection(int institutionId, string name, string code)
    {
        InstitutionId = institutionId;
        Name = name;
        Code = code;
    }

    public string Name { get; private set; }
    public string Code { get; private set; }
    public DateTime? DeletedDate { get; private set; }
    public int InstitutionId { get; private set; }
    public List<CollectionTask> Tasks { get; private set; } = new();
    public List<Specimen> Specimens { get; private set; } = new();
}

