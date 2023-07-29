using Sparc.Blossom.Data;
using Torch.Web.Users;
using Torch.Web.Workflows;

namespace Torch.Web.Institutions;

public class Institution : Entity<int>
{
    public Institution(string name, string code)
    {
        Name = name;
        Code = code;
        CreatedDate = DateTime.UtcNow;
    }

    public string Name { get; private set; }
    public string Code { get; private set; }
    public DateTime CreatedDate { get; private set; }
    public DateTime? DeletedDate { get; private set; }
    public int OwnerId { get; private set; }
    public List<Workflow> Workflows { get; private set; } = new();
    public User Owner { get; private set; } = null!;
}

