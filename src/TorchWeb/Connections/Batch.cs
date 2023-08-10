namespace Torch.Web.Workflows;

public record Batch(string Id, DateTime CreateDate, int SpecimenCount)
{
    public static string NewId(string hostDirectory)
    {
        return $"{GetRandomWord(hostDirectory)}-{GetRandomWord(hostDirectory)}";
    }

    static string GetRandomWord(string hostDirectory)
    {
        var random = new Random();
        var word = File.ReadLines(Path.Combine(hostDirectory, "_Plugins/words_alpha.txt"))
            .Skip(random.Next(370000))
            .First()
            .Trim()
            .ToLower();

        // Check against office-unsafe words
        if (File.ReadLines(Path.Combine(hostDirectory, "_Plugins/words_officesafe.txt"))
            .Any(x => x.ToLower() == word))
            return GetRandomWord(hostDirectory);

        return word;
    }
}

