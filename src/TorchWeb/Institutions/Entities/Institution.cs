using Sparc.Blossom.Data;
using Torch.Web.Collections;
using Torch.Web.Users;

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
    public List<Collection> Collections { get; private set; } = new();
    public List<User> Users { get; private set; } = new();
}

