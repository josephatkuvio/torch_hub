using Microsoft.AspNetCore.Components.Authorization;
using Microsoft.EntityFrameworkCore;
using Sparc.Blossom.Authentication;
using Sparc.Blossom.Data;
using System.Security.Claims;
using Torch.Web.Users;
using Torch.Web.Workflows;

namespace Torch.Web._Plugins;

public class TorchAuthenticator
{
    public TorchAuthenticator(AuthenticationStateProvider auth, IRepository<User> users, IRepository<Workflow> workflows)
    {
        Auth = auth;
        Users = users;
        Workflows = workflows;
    }

    public AuthenticationStateProvider Auth { get; }
    public IRepository<User> Users { get; }
    public IRepository<Workflow> Workflows { get; }

    public async Task<User?> LoginAsync()
    {
        var auth = await Auth.GetAuthenticationStateAsync();
        if (auth?.User?.Identity?.IsAuthenticated == true)
        {
            var provider = auth.User.Get(ClaimTypes.NameIdentifier)
                ?? throw new Exception("Missing provider information in user claims.");

            var providerName = provider.Split('|').First();
            var providerId = provider.Split('|').Last();
            //var user = Users.Query.FirstOrDefault(x => x.Identities.Any(y => y.ProviderName == providerName && y.ProviderId == providerId));
            var user = Users.Include("WorkflowUsers.Workflow.Institution", "CurrentWorkflow")
                .FirstOrDefault(x => x.Identities.Any(y => y.ProviderName == providerName && y.ProviderId == providerId));

            if (user == null)
            {
                var email = auth.User.Get(ClaimTypes.Email) ?? auth.User.Get(ClaimTypes.Name) ?? auth.User.Get("name");
                user = Users.Query.FirstOrDefault(x => x.Email == email);
                if (user == null)
                {
                    user = new(auth.User);
                    user.AddIdentity(providerName, providerId);
                    await Users.AddAsync(user);
                }
                else
                {
                    user.AddIdentity(providerName, providerId);
                    await Users.UpdateAsync(user);
                }
            }

            if (user.CurrentWorkflowId == null)
            {
                var workflow = user.CreateDefaultWorkflow();
                await Workflows.UpdateAsync(workflow);
                user.SetCurrentWorkflow(workflow);
            }
            else
            {
                user.SetCurrentWorkflow(user.CurrentWorkflow!);
            }

            await Users.UpdateAsync(user);
            await Users.ExecuteAsync(user, u => u.Login());
            return user;
        }

        return null;
    }
}
