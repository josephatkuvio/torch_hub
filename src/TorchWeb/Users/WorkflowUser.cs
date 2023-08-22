using Torch.Web.Users;

namespace Torch.Web.Workflows;

public class WorkflowUser
{
    private WorkflowUser()
    {
        Role = "";
    }
    
    public WorkflowUser(Workflow workflow, User user, string role)
    {
        Workflow = workflow;
        WorkflowId = workflow.Id;
        User = user;
        UserId = user.Id;
        Role = role;
        CreatedDate = DateTime.UtcNow;
    }

    public int WorkflowId { get; private set; }
    public int UserId { get; private set; }
    public DateTime CreatedDate { get; private set; }
    public string Role { get; private set; }
    public Workflow Workflow { get; private set; } = null!;
    public User User { get; private set; } = null!;
}

