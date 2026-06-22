package com.umbrellaos.plugin.listeners;

import com.umbrellaos.plugin.api.CoreApiClient;
import com.umbrellaos.plugin.managers.PunishmentManager;
import com.umbrellaos.plugin.managers.VerificationManager;
import org.bukkit.Bukkit;
import org.bukkit.entity.Player;
import org.bukkit.plugin.Plugin;
import org.bukkit.event.EventHandler;
import org.bukkit.event.EventPriority;
import org.bukkit.event.Listener;
import org.bukkit.event.player.AsyncPlayerPreLoginEvent;
import org.bukkit.event.player.PlayerJoinEvent;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

public class PlayerJoinListener implements Listener {
    private final CoreApiClient apiClient;
    private final VerificationManager verificationManager;
    private final PunishmentManager punishmentManager;
    private final boolean verifyOnJoin;

    public PlayerJoinListener(CoreApiClient apiClient, VerificationManager verificationManager,
                              PunishmentManager punishmentManager, boolean verifyOnJoin) {
        this.apiClient = apiClient;
        this.verificationManager = verificationManager;
        this.punishmentManager = punishmentManager;
        this.verifyOnJoin = verifyOnJoin;
    }

    @EventHandler(priority = EventPriority.HIGH)
    public void onPreLogin(AsyncPlayerPreLoginEvent event) {
        UUID uuid = event.getUniqueId();
        String username = event.getName();
        String ipAddress = event.getAddress().getHostAddress();

        try {
            punishmentManager.refreshSync(uuid);
            if (punishmentManager.isBanned(uuid)) {
                String reason = punishmentManager.getBanReason(uuid);
                event.disallow(AsyncPlayerPreLoginEvent.Result.KICK_BANNED,
                    "\u00a7cYou are banned: " + (reason != null ? reason : "No reason provided"));
                return;
            }
        } catch (Exception e) {
            e.printStackTrace();
        }

        if (verifyOnJoin) {
            try {
                Boolean isVerified = apiClient.checkVerificationStatus(uuid.toString()).get();
                if (!Boolean.TRUE.equals(isVerified)) {
                    String rawResponse = apiClient.requestVerification(uuid.toString(), username, ipAddress).get();
                    String code;
                    try {
                        com.google.gson.JsonObject json = com.google.gson.JsonParser.parseString(rawResponse).getAsJsonObject();
                        code = json.get("code").getAsString();
                    } catch (Exception ex) {
                        code = rawResponse;
                    }
                    event.disallow(AsyncPlayerPreLoginEvent.Result.KICK_OTHER,
                        "\u00a76\u00a7lVerification Required\n\n" +
                        "\u00a7eSend this code to \u00a7bMoonBot\u00a7e on Discord:\n\n" +
                        "\u00a7f\u00a7l" + code + "\n\n" +
                        "\u00a77Join: \u00a7bdiscord.gg/p4w7um77JG\n" +
                        "\u00a77Rejoin after verifying.");
                    return;
                }
            } catch (Exception e) {
                e.printStackTrace();
                event.disallow(AsyncPlayerPreLoginEvent.Result.KICK_OTHER,
                    "\u00a7cVerification check failed. Please try again.");
                return;
            }
        }
    }

    @EventHandler(priority = EventPriority.MONITOR)
    public void onPlayerJoin(PlayerJoinEvent event) {
        Player player = event.getPlayer();
        String ipAddress = player.getAddress().getAddress().getHostAddress();
        String uuid = player.getUniqueId().toString();
        String username = player.getName();
        Plugin umbrellaPlugin = Bukkit.getPluginManager().getPlugin("UmbrellaOS");

        Map<String, Object> metadata = new HashMap<>();
        metadata.put("ip", ipAddress);
        apiClient.postEvent("player_join", uuid, username, metadata).exceptionally(e -> {
            e.printStackTrace();
            return null;
        });

        Bukkit.getScheduler().runTaskAsynchronously(umbrellaPlugin, () -> {
            apiClient.checkAltDetection(uuid, ipAddress, username).exceptionally(e -> {
                e.printStackTrace();
                return null;
            });
        });
    }
}
