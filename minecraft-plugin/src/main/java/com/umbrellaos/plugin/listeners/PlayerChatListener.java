package com.umbrellaos.plugin.listeners;

import com.umbrellaos.plugin.api.CoreApiClient;
import com.umbrellaos.plugin.managers.BridgeManager;
import com.umbrellaos.plugin.managers.PunishmentManager;
import com.umbrellaos.plugin.managers.VerificationManager;
import io.papermc.paper.chat.ChatRenderer;
import io.papermc.paper.event.player.AsyncChatEvent;
import net.kyori.adventure.text.Component;
import net.kyori.adventure.text.format.NamedTextColor;
import net.kyori.adventure.text.serializer.plain.PlainTextComponentSerializer;
import org.bukkit.Bukkit;
import org.bukkit.entity.Player;
import org.bukkit.event.EventHandler;
import org.bukkit.event.Listener;
import java.time.Duration;
import java.time.OffsetDateTime;

public class PlayerChatListener implements Listener {
    private final CoreApiClient apiClient;
    private final VerificationManager verificationManager;
    private final BridgeManager bridgeManager;
    private final PunishmentManager punishmentManager;

    public PlayerChatListener(CoreApiClient apiClient, VerificationManager verificationManager,
                              BridgeManager bridgeManager, PunishmentManager punishmentManager) {
        this.apiClient = apiClient;
        this.verificationManager = verificationManager;
        this.bridgeManager = bridgeManager;
        this.punishmentManager = punishmentManager;
    }

    private static String formatRemaining(OffsetDateTime expiry) {
        Duration remaining = Duration.between(OffsetDateTime.now(), expiry);
        if (remaining.isNegative()) return "expiring shortly";
        long hours = remaining.toHours();
        long minutes = remaining.toMinutes() % 60;
        if (hours > 0) return hours + "h " + minutes + "m remaining";
        return minutes + "m remaining";
    }

    @EventHandler
    public void onAsyncPlayerChat(AsyncChatEvent event) {
        Player player = event.getPlayer();
        String uuid = player.getUniqueId().toString();
        String message = PlainTextComponentSerializer.plainText().serialize(event.message());

        // Check if player is in verification limbo
        if (verificationManager.isInLimbo(player.getUniqueId())) {
            event.setCancelled(true);
            player.sendMessage(Component.text("§cYou must verify your account before chatting!").color(NamedTextColor.RED));
            return;
        }

        // Check mute status — enforced server-side, independent of Discord
        if (punishmentManager.isMuted(player.getUniqueId())) {
            event.setCancelled(true);
            String reason = punishmentManager.getMuteReason(player.getUniqueId());
            OffsetDateTime expiry = punishmentManager.getMuteExpiry(player.getUniqueId());
            String timeLeft = expiry != null ? formatRemaining(expiry) : "permanently";
            player.sendMessage(Component.text(
                "§cYou are muted" + (reason != null ? " for: " + reason : "") + " (" + timeLeft + ")."
            ).color(NamedTextColor.RED));
            return;
        }

        // Check bridge mode
        String bridgeMode = bridgeManager.getBridgeMode();
        if ("full".equalsIgnoreCase(bridgeMode)) {
            // Full bridge mode: send all chat to Discord, don't show in-game
            event.setCancelled(true);
            apiClient.postBridgeMessage("minecraft", uuid, message).exceptionally(e -> {
                e.printStackTrace();
                return null;
            });
        }
        // Partial mode: let chat through normally, they use /disc command
        // Off mode: let chat through normally
    }
}
