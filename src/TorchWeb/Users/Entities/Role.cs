namespace Torch.Web.Users;

public class Role
{
    public Role(string name)
    {
        Name = name;
    }
    
    public int Id { get; private set; }
    public string Name { get; private set; }
    public string? Description { get; private set; }
    public List<User> Users { get; private set; } = new();
}