using Torch.Web.Users;

namespace Torch.Web.Collections;

public class CollectionUser
{
    public CollectionUser(int collectionId, int userId, string role)
    {
        CollectionId = collectionId;
        UserId = userId;
        Role = role;
    }

    public int CollectionId { get; private set; }
    public int UserId { get; private set; }
    public string Role { get; private set; }
    public Collection Collection { get; private set; } = null!;
    public User User { get; private set; } = null!;
}

