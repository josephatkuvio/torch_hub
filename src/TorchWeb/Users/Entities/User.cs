using Sparc.Blossom.Data;
using Torch.Web.Institutions;
using Torch.Web.Workflows;

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
    public Institution? Institution { get; private set; }
    public List<Identity> Identities { get; private set; } = new();
    public List<WorkflowUser> WorkflowUsers { get; private set; } = new();

    public void SetInstitution(int? id) => InstitutionId = id;
    public bool IsInRole(string role, int workflowId) => WorkflowUsers.Any(x => x.WorkflowId == workflowId && x.Role == role);
}

