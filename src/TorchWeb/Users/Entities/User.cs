using Sparc.Blossom.Authentication;
using Sparc.Blossom.Data;
using System.Security.Claims;
using System.Security.Principal;
using Torch.Web.Institutions;
using Torch.Web.Workflows;

namespace Torch.Web.Users;

public class User : Entity<int>
{
    public User()
    {
    }
  
    public User(ClaimsPrincipal user)
    {
        Email = user.Get(ClaimTypes.Email) ?? user.Get(ClaimTypes.Name) ?? user.Get("name");
        FirstName = user.Get(ClaimTypes.GivenName);
        LastName = user.Get(ClaimTypes.Surname);
        IsAuthenticated = user.Identity?.IsAuthenticated ?? false;
    }

    public string Email { get; private set; }
    public string? FirstName { get; private set; }
    public string? LastName { get; private set; }
    internal bool IsAuthenticated { get; }
    public int? InstitutionId { get; private set; }
    public DateTime LastLoginDate { get; private set; }
    public Institution? Institution { get; private set; }
    public List<Identity> Identities { get; private set; } = new();
    public List<WorkflowUser> WorkflowUsers { get; private set; } = new();

    public void AddIdentity(string providerName, ClaimsPrincipal user)
    {
        var providerId = user.Get(ClaimTypes.NameIdentifier);
        if (providerId != null)
        {
            Identities.Add(new Identity(Id, providerName, providerId));
        }
    }

    public void SetInstitution(int? id) => InstitutionId = id;
    public bool IsInRole(string role, int workflowId) => WorkflowUsers.Any(x => x.WorkflowId == workflowId && x.Role == role);

    internal void Login()
    {
        LastLoginDate = DateTime.UtcNow;
    }
}

