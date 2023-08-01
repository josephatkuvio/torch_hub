using Sparc.Blossom.Authentication;
using Sparc.Blossom.Data;
using System.Security.Claims;
using System.Security.Principal;
using Torch.Web.Institutions;
using Torch.Web.Workflows;
using static Microsoft.EntityFrameworkCore.DbLoggerCategory.Database;
using Torch.Web.Workflows.Connections;

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

        if (Email!.Contains(' ') && FirstName == null)
        {
            var parts = Email.Split(' ');
            FirstName = parts[0];
            LastName = parts[1];
        }

        IsAuthenticated = user.Identity?.IsAuthenticated ?? false;
    }

    public string Email { get; private set; }
    public string? FirstName { get; private set; }
    public string? LastName { get; private set; }
    internal bool IsAuthenticated { get; }
    public int? CurrentWorkflowId { get; private set; }
    public DateTime LastLoginDate { get; private set; }
    public Workflow? CurrentWorkflow { get; private set; }
    public List<Identity> Identities { get; private set; } = new();
    public List<WorkflowUser> WorkflowUsers { get; private set; } = new();

    public void AddIdentity(string providerName, string providerId)
    {
        if (!Identities.Any(x => x.ProviderName == providerName && x.ProviderId == providerId))
            Identities.Add(new Identity(Id, providerName, providerId));
    }

    public void SetCurrentWorkflow(Workflow workflow)
    {
        CurrentWorkflow = workflow;
        CurrentWorkflowId = workflow.Id;
    }

    public bool IsInRole(string role, int workflowId) => WorkflowUsers.Any(x => x.WorkflowId == workflowId && x.Role == role);

    internal void Login()
    {
        LastLoginDate = DateTime.UtcNow;
    }

    internal Workflow CreateDefaultWorkflow()
    {
        if (CurrentWorkflow != null)
            return CurrentWorkflow;

        var institution = new Institution("My Workspace", Email);
        institution.SetOwner(this);

        var workflow = new Workflow(institution, "My First Workflow", "Set up your first workflow");
        institution.Workflows.Add(workflow);

        workflow.Connections.Add(new AzureBlobConnection(workflow, "Input"));
        workflow.Connections.Add(new AzureBlobConnection(workflow, "Output"));

        return workflow;
    }
}

