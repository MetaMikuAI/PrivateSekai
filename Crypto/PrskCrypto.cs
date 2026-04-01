using System.Buffers;
using System.Security.Cryptography;
using System.Text.Json;
using MessagePack;
using PrivateSekai.Config;

namespace PrivateSekai.Crypto;

public static class PrskCrypto
{
    public static byte[] EncryptAesCbc(byte[] data)
    {
        using var aes = Aes.Create();
        aes.Key = ServerConfig.AesKey;
        aes.IV  = ServerConfig.AesIv;
        aes.Mode    = CipherMode.CBC;
        aes.Padding = PaddingMode.PKCS7;

        using var encryptor = aes.CreateEncryptor();
        return encryptor.TransformFinalBlock(data, 0, data.Length);
    }

    public static byte[] DecryptAesCbc(byte[] data)
    {
        using var aes = Aes.Create();
        aes.Key = ServerConfig.AesKey;
        aes.IV  = ServerConfig.AesIv;
        aes.Mode    = CipherMode.CBC;
        aes.Padding = PaddingMode.PKCS7;

        using var decryptor = aes.CreateDecryptor();
        return decryptor.TransformFinalBlock(data, 0, data.Length);
    }

    /// <summary>
    /// T → MessagePack bytes → AES-CBC encrypt
    /// </summary>
    public static byte[] PrskEnc<T>(T data)
    {
        byte[] msgpack = MessagePackSerializer.Serialize(data);
        return EncryptAesCbc(msgpack);
    }

    /// <summary>
    /// T → JSON (skip null) → MessagePack bytes (Float32) → AES-CBC encrypt
    /// 用于含 SuiteUser 等大量可空字段的响应，序列化时跳过 null
    /// </summary>
    public static byte[] PrskEncSkipNull<T>(T data)
    {
        var json = JsonSerializer.Serialize(data, _skipNullOptions);
        return PrskEncFromJson(json);
    }

    private static readonly JsonSerializerOptions _skipNullOptions = new()
    {
        DefaultIgnoreCondition = System.Text.Json.Serialization.JsonIgnoreCondition.WhenWritingNull,
        IncludeFields = true
    };

    /// <summary>
    /// AES-CBC decrypt → MessagePack bytes → T
    /// </summary>
    public static T PrskDec<T>(byte[] data)
    {
        byte[] decrypted = DecryptAesCbc(data);
        return MessagePackSerializer.Deserialize<T>(decrypted);
    }

    /// <summary>
    /// JSON string → MessagePack bytes (Float32) → AES-CBC encrypt
    /// 用于 SuiteMasterFile 等无固定类型的场景
    /// 使用 Float32 编码浮点数，与 Python msgpack.packb(use_single_float=True) 行为一致
    /// </summary>
    public static byte[] PrskEncFromJson(string json)
    {
        byte[] msgpack = ConvertJsonToMsgPackSingleFloat(json);
        return EncryptAesCbc(msgpack);
    }

    /// <summary>
    /// 手动将 JSON 转为 MessagePack，浮点数使用 Float32（单精度）
    /// 对应 Python: msgpack.packb(data, use_bin_type=True, use_single_float=True)
    /// </summary>
    private static byte[] ConvertJsonToMsgPackSingleFloat(string json)
    {
        var buffer = new ArrayBufferWriter<byte>();
        var writer = new MessagePackWriter(buffer);

        using var doc = JsonDocument.Parse(json);
        WriteElement(ref writer, doc.RootElement);

        writer.Flush();
        return buffer.WrittenSpan.ToArray();
    }

    private static void WriteElement(ref MessagePackWriter writer, JsonElement element)
    {
        switch (element.ValueKind)
        {
            case JsonValueKind.Object:
            {
                var count = 0;
                foreach (var _ in element.EnumerateObject()) count++;
                writer.WriteMapHeader(count);
                foreach (var prop in element.EnumerateObject())
                {
                    writer.Write(prop.Name);
                    WriteElement(ref writer, prop.Value);
                }
                break;
            }
            case JsonValueKind.Array:
                writer.WriteArrayHeader(element.GetArrayLength());
                foreach (var item in element.EnumerateArray())
                    WriteElement(ref writer, item);
                break;
            case JsonValueKind.String:
                writer.Write(element.GetString());
                break;
            case JsonValueKind.Number:
                if (element.TryGetInt64(out var longVal))
                    writer.Write(longVal);
                else
                    writer.Write((float)element.GetDouble()); // Single precision (Float32)
                break;
            case JsonValueKind.True:
                writer.Write(true);
                break;
            case JsonValueKind.False:
                writer.Write(false);
                break;
            default: // Null, Undefined
                writer.WriteNil();
                break;
        }
    }
}
