using Sparc.Blossom.Data;
using Torch.Web.Institutions;

namespace Torch.Web.Users;

public class User : Entity<int>
{
    public User(string email)
    {
        Email = email;
    }
    
    public string Email { get; private set; }
    public string? Password { get; private set; }
    public string? FirstName { get; private set; }
    public string? LastName { get; private set; }
    public bool Active { get; private set; }
    public DateTime? ConfirmedAt { get; private set; }
    public int? InstitutionId { get; private set; }
    public Institution Institution { get; private set; } = null!;
    public List<Role> Roles { get; private set; } = new();

    public void SetInstitution(int? id) => InstitutionId = id;
}

