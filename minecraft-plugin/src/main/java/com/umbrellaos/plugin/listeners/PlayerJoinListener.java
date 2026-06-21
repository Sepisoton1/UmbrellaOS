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
import org.bukkit.event.player.PlayerJoinEvent;

import java.util.HashMap;
import java.util.Map;

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

    @EventHandler(priority = EventPriority.MONITOR)
    public void onPlayerJoin(PlayerJoinEvent event) {
        Player player = event.getPlayer();
        String ipAddress = player.getAddress().getAddress().getHostAddress();
        String uuid = player.getUniqueId().toString();
        String username = player.getName();

        Plugin umbrellaPlugin = Bukkit.getPluginManager().getPlugin("UmbrellaOS");

        // Refresh punishments off the main thread (blocking HTTP call), then
        // act on the result back on the main thread. This fixes a race where
        // refresh() returned immediately while isBanned() ran on stale/empty
        // cache data, letting banned players through.
        Bukkit.getScheduler().runTaskAsynchronously(umbrellaPlugin, () -> {
            punishmentManager.refreshSync(player.getUniqueId());

            Bukkit.getScheduler().runTask(umbrellaPlugin, () -> {
                if (!player.isOnline()) return;
                boolean banned = punishmentManager.isBanned(player.getUniqueId());
                Bukkit.getLogger().info("[UmbrellaOS] Punishment check for " + player.getName() + " (" + player.getUniqueId() + "): banned=" + banned);
                if (banned) {
                    String reason = punishmentManager.getBanReason(player.getUniqueId());
                    player.kickPlayer("§cYou are banned: " + (reason != null ? reason : "No reason provided"));
                }
            });
        });

        // Check verification status if verify on join is enabled
        if (verifyOnJoin) {
            Bukkit.getScheduler().runTaskAsynchronously(Bukkit.getPluginManager().getPlugin("UmbrellaOS"), () -> {
                try {
                    Boolean isVerified = apiClient.checkVerificationStatus(uuid).get();
                    if (!Boolean.TRUE.equals(isVerified)) {
                        // Player is not verified, put in limbo
                        Bukkit.getScheduler().runTask(Bukkit.getPluginManager().getPlugin("UmbrellaOS"), () -> {
                            try {
                                String code = apiClient.requestVerification(uuid, username, ipAddress).get();
                                verificationManager.putInLimbo(player.getUniqueId(), code);
                            } catch (Exception e) {
                                e.printStackTrace();
                            }
                        });
                    }
                } catch (Exception e) {
                    e.printStackTrace();
                }
            });
        }

        // Post join event
        Map<String, Object> metadata = new HashMap<>();
        metadata.put("ip", ipAddress);
        apiClient.postEvent("player_join", uuid, username, metadata).exceptionally(e -> {
            e.printStackTrace();
            return null;
        });

        // Check alt detection asynchronously
        Bukkit.getScheduler().runTaskAsynchronously(Bukkit.getPluginManager().getPlugin("UmbrellaOS"), () -> {
            apiClient.checkAltDetection(uuid, ipAddress, username).exceptionally(e -> {
                e.printStackTrace();
                return null;
            });
        });
    }
}
