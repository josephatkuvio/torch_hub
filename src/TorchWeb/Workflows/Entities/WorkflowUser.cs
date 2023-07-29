using Torch.Web.Users;

namespace Torch.Web.Workflows;

public class WorkflowUser
{
    public WorkflowUser(int workflowId, int userId, string role)
    {
        WorkflowId = workflowId;
        UserId = userId;
        Role = role;
    }

    public int WorkflowId { get; private set; }
    public int UserId { get; private set; }
    public string Role { get; private set; }
    public Workflow Workflow { get; private set; } = null!;
    public User User { get; private set; } = null!;
}

