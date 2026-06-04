using System.Text;

namespace PrivateSekai.Config;

public static class ServerConfig
{
    public static byte[] AesKey { get; private set; } = null!;
    public static byte[] AesIv  { get; private set; } = null!;
    public static string JwtKey { get; private set; } = null!;
    public static byte[] EmptyRequestCiphertext { get; private set; } = null!;

    public static bool IgnoreInvalidCredential { get; private set; }
    public static bool SkipTutorial { get; private set; }
    public static bool Debug { get; private set; }

    public static int Port { get; private set; }

    public static string GameVersionDomain { get; private set; } = null!;

    public static string TemplatePath { get; private set; } = null!;
    public static string SuiteMasterFilePath { get; private set; } = null!;
    public static string SekaiMasterDbDiffPath { get; private set; } = null!;

    public static void Load(IConfiguration config)
    {
        var s = config.GetSection("PrivateSekai");
        if (!s.Exists())
            throw new InvalidOperationException("Missing 'PrivateSekai' section in appsettings.json");

        AesKey      = Encoding.UTF8.GetBytes(Require(s, "AesKey"));
        AesIv       = Encoding.UTF8.GetBytes(Require(s, "AesIv"));
        JwtKey      = Require(s, "JwtKey");
        EmptyRequestCiphertext = Convert.FromHexString(Require(s, "EmptyRequestCiphertext"));

        IgnoreInvalidCredential = bool.Parse(Require(s, "IgnoreInvalidCredential"));
        SkipTutorial            = bool.Parse(Require(s, "SkipTutorial"));
        Debug                   = bool.Parse(Require(s, "Debug"));
        Port                    = int.Parse(Require(s, "Port"));

        GameVersionDomain        = Require(s, "GameVersionDomain");

        var paths = s.GetSection("Paths");
        TemplatePath          = Require(paths, "Template");
        SuiteMasterFilePath   = Require(paths, "SuiteMasterFile");
        SekaiMasterDbDiffPath = Require(paths, "SekaiMasterDbDiff");
    }

    private static string Require(IConfigurationSection section, string key) =>
        section[key] ?? throw new InvalidOperationException(
            $"Missing required config: PrivateSekai:{key}");
}
