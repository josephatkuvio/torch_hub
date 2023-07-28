using Sparc.Blossom.Data;
using Torch.Web.Collections;
using Torch.Web.Institutions;

namespace Torch.Web.Users;

public class User : Entity<int>
{
    public User(string email)
    {
        Email = email;
    }
    
    public string Email { get; private set; }
    public string? FirstName { get; private set; }
    public string? LastName { get; private set; }
    public int? InstitutionId { get; private set; }
    public Institution Institution { get; private set; } = null!;
    public List<Role> Roles { get; private set; } = new();
    public List<CollectionUser> Collections { get; private set; } = new();

    public void SetInstitution(int? id) => InstitutionId = id;
    public bool IsInRole(string role) => Roles.Any(r => r.Name == role);
    public bool IsInRole(string role, int collectionId) => Collections.Any(x => x.CollectionId == collectionId && x.Role == role);
}

