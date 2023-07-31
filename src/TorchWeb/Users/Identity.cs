namespace Torch.Web.Users;

public class Identity
{
    public Identity(int userId, string providerName, string providerId)
    {
        UserId = userId;
        ProviderName = providerName;
        ProviderId = providerId;
    }
    
    public int Id { get; set; }
    public int UserId { get; set; }
    public string ProviderName { get; set; }
    public string ProviderId { get; set; }
    public User User { get; set; } = null!;
}

