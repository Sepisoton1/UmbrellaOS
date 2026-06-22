path = r'minecraft-plugin\src\main\java\com\umbrellaos\plugin\api\CoreApiClient.java'
with open(path, encoding='utf-8') as f:
    content = f.read()

# Fix 1: username -> player_username in requestVerification
old = 'body.addProperty("username", username);'
new = 'body.addProperty("player_username", username);'
if old in content:
    content = content.replace(old, new)
    print('requestVerification fixed')
else:
    print('requestVerification - not found, already fixed?')

# Fix 2: player_uuid -> minecraft_uuid in postSnapshot
old2 = '        body.addProperty("player_uuid", playerUuid);\n        return asyncPost("/api/v1/snapshots"'
new2 = '        body.addProperty("minecraft_uuid", playerUuid);\n        return asyncPost("/api/v1/snapshots"'
if old2 in content:
    content = content.replace(old2, new2)
    print('postSnapshot uuid fixed')
else:
    print('postSnapshot - not found, checking alternate...')
    old3 = 'body.addProperty("player_uuid", playerUuid);\n        return asyncPost("/api/v1/snapshots'
    if old3 in content:
        content = content.replace(old3, 'body.addProperty("minecraft_uuid", playerUuid);\n        return asyncPost("/api/v1/snapshots')
        print('postSnapshot uuid fixed (alt)')

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('Done')
