package com.umbrellaos.plugin.listeners;

import com.umbrellaos.plugin.UmbrellaPlugin;
import com.umbrellaos.plugin.api.CoreApiClient;
import com.umbrellaos.plugin.managers.AnticheatManager;
import com.umbrellaos.plugin.managers.PunishmentManager;
import org.bukkit.Bukkit;
import org.bukkit.entity.Player;
import org.bukkit.event.Event;
import org.bukkit.event.EventPriority;
import org.bukkit.event.Listener;

import java.lang.reflect.Method;
import java.util.UUID;

/** Listens to GrimAC PunishmentEvent via reflection (soft dependency). */
public class GrimFlagListener implements Listener {
    private final AnticheatManager anticheatManager;
    private final PunishmentManager punishmentManager;

    public GrimFlagListener(AnticheatManager anticheatManager, PunishmentManager punishmentManager) {
        this.anticheatManager = anticheatManager;
        this.punishmentManager = punishmentManager;
    }

    public static void register(UmbrellaPlugin plugin, AnticheatManager anticheatManager,
                                PunishmentManager punishmentManager) {
        if (Bukkit.getPluginManager().getPlugin("GrimAC") == null) {
            plugin.getLogger().info("GrimAC not found -- anticheat bridge disabled");
            return;
        }
        try {
            Class<?> eventClass = Class.forName("ac.grim.grimac.api.event.events.PunishmentEvent");
            GrimFlagListener listener = new GrimFlagListener(anticheatManager, punishmentManager);
            Bukkit.getPluginManager().registerEvent(
                    (Class<? extends Event>) eventClass,
                    listener,
                    EventPriority.MONITOR,
                    (l, event) -> ((GrimFlagListener) l).onGrimPunish(event),
                    plugin,
                    false
            );
            plugin.getLogger().info("GrimAC anticheat bridge registered");
        } catch (ClassNotFoundException e) {
            plugin.getLogger().warning("GrimAC API not found: " + e.getMessage());
        }
    }

    public void onGrimPunish(Event event) {
        try {
            Method getPlayer = event.getClass().getMethod("getPlayer");
            Object grimPlayer = getPlayer.invoke(event);
            Method getUuid = grimPlayer.getClass().getMethod("getUniqueId");
            UUID uuid = (UUID) getUuid.invoke(grimPlayer);
            Method getName = grimPlayer.getClass().getMethod("getName");
            String username = String.valueOf(getName.invoke(grimPlayer));

            String checkName = "Unknown";
            try {
                Object check = event.getClass().getMethod("getCheck").invoke(event);
                checkName = String.valueOf(check.getClass().getMethod("getCheckName").invoke(check));
            } catch (ReflectiveOperationException ignored) {
                try {
                    checkName = String.valueOf(event.getClass().getMethod("getSimpleCheckName").invoke(event));
                } catch (ReflectiveOperationException ignored2) { }
            }

            String verbose = "";
            try {
                verbose = String.valueOf(event.getClass().getMethod("getVerbose").invoke(event));
            } catch (ReflectiveOperationException ignored) {
                verbose = checkName;
            }

            int vl = 0;
            try {
                vl = (int) event.getClass().getMethod("getVl").invoke(event);
            } catch (ReflectiveOperationException ignored) { }

            final String finalCheckName = checkName;
            final String finalVerbose = verbose;
            final int finalVl = vl;
            final String finalUsername = username;

            anticheatManager.handleFlag(uuid, username, checkName, verbose, vl).thenAccept(result -> {
                String action = String.valueOf(result.getOrDefault("action", "tempban"));
                String reason = String.valueOf(result.getOrDefault("reason", "[Grim] " + finalCheckName));
                String displayUser = String.valueOf(result.getOrDefault("username", uuid.toString()));
                double confidence = 0.0;
                try { confidence = Double.parseDouble(String.valueOf(result.getOrDefault("ai_confidence", "0.0"))); } catch (Exception ignored) {}
                final double finalConf = confidence;

                org.bukkit.plugin.Plugin plugin = Bukkit.getPluginManager().getPlugin("UmbrellaOS");

                Bukkit.getScheduler().runTask(plugin, () -> {
                    // Notify online staff in-game
                    String confStr = String.format("%.0f%%", finalConf * 100);
                    String staffMsg = "\u00a7e[AC] \u00a7f" + displayUser
                            + " \u00a77flagged: \u00a7e" + finalCheckName
                            + " \u00a77VL:\u00a7c" + finalVl
                            + " \u00a77conf:\u00a76" + confStr
                            + " \u00a77-> \u00a7c" + action.toUpperCase();
                    for (Player online : Bukkit.getOnlinePlayers()) {
                        if (online.hasPermission("umbrellaos.staff")) {
                            online.sendMessage(staffMsg);
                        }
                    }

                    Player player = Bukkit.getPlayer(uuid);
                    if (player == null) return;

                    switch (action) {
                        case "warn":
                            player.sendMessage("\u00a7e[Anti-Cheat] \u00a7fFlagged for \u00a7e"
                                    + finalCheckName + "\u00a7f. Play fairly.");
                            break;

                        case "kick":
                            player.kickPlayer("\u00a7c[Anti-Cheat] Kicked for suspicious activity: "
                                    + finalCheckName
                                    + "\n\u00a77This is not a ban. You may rejoin.");
                            break;

                        case "tempban":
                        default:
                            punishmentManager.refresh(uuid);
                            Bukkit.getScheduler().runTaskLater(plugin, () -> {
                                Player p2 = Bukkit.getPlayer(uuid);
                                if (p2 != null) {
                                    p2.kickPlayer("\u00a7c[Anti-Cheat] You have been temporarily banned."
                                            + "\n\u00a77Reason: " + reason
                                            + "\n\u00a77Appeal in our Discord server.");
                                }
                            }, 10L);
                            break;
                    }
                });
            });
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
