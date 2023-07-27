using System.Security.Claims;

namespace Torch.Web._Plugins;

public static class UserClaimsExtensions
{
    public static int? InstitutionId(this ClaimsPrincipal user)
        => user.Claim("institution_id") != null
        ? int.Parse(user.Claim("institution_id")!)
        : null;

    public static string? Claim(this ClaimsPrincipal user, string claimType)
        =>
        user.HasClaim(x => x.Type == claimType) == true ?
            user.Claims.First(x => x.Type == claimType).Value
            : null;
}
