using Microsoft.AspNetCore.Components.Authorization;
using Sparc.Blossom.Authentication;
using Sparc.Blossom.Data;
using System.Security.Claims;
using Torch.Web.Users;

namespace Torch.Web._Plugins;

public class TorchAuthenticator
{
    public TorchAuthenticator(AuthenticationStateProvider auth, IRepository<User> users)
    {
        Auth = auth;
        Users = users;
    }

    public AuthenticationStateProvider Auth { get; }
    public IRepository<User> Users { get; }

    public async Task<User?> LoginAsync()
    {
        var auth = await Auth.GetAuthenticationStateAsync();
        if (auth?.User != null)
        {
            var providerId = auth.User.Get(ClaimTypes.NameIdentifier);
            var user = Users.Query.FirstOrDefault(x => x.Identities.Any(y => y.ProviderName == "auth0" && y.ProviderId == providerId));
            if (user == null)
            {
                var email = auth.User.Get(ClaimTypes.Email) ?? auth.User.Get(ClaimTypes.Name) ?? auth.User.Get("name");
                user = Users.Query.FirstOrDefault(x => x.Email == email);
                if (user == null)
                {
                    user = new(auth.User);
                    user.AddIdentity("auth0", auth.User);
                    await Users.AddAsync(user);
                }
                else
                {
                    user.AddIdentity("auth0", auth.User);
                    await Users.UpdateAsync(user);
                }
            }

            await Users.ExecuteAsync(user, u => u.Login());
            return user;
        }

        return null;
    }
}
