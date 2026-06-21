package com.umbrellaos.plugin.commands;

import com.umbrellaos.plugin.api.CoreApiClient;
import org.bukkit.Bukkit;
import org.bukkit.command.Command;
import org.bukkit.command.CommandExecutor;
import org.bukkit.command.CommandSender;
import org.bukkit.entity.Player;

public class UmbrellaFlagCommand implements CommandExecutor {
    private final CoreApiClient apiClient;

    public UmbrellaFlagCommand(CoreApiClient apiClient) {
        this.apiClient = apiClient;
    }

    @Override
    public boolean onCommand(CommandSender sender, Command command, String label, String[] args) {
        if (args.length < 3) return false;
        String playerName = args[0];
        String checkName = args[1];
        int vl;
        try { vl = Integer.parseInt(args[2]); } catch (NumberFormatException e) { vl = 0; }

        Player target = Bukkit.getPlayer(playerName);
        if (target == null) return true;

        final int finalVl = vl;
        apiClient.postAnticheatFlag(target.getUniqueId().toString(), target.getName(), checkName, "", finalVl)
            .thenAccept(response -> {
                Boolean shouldKick = (Boolean) response.get("kick");
                if (Boolean.TRUE.equals(shouldKick)) {
                    Bukkit.getScheduler().runTask(Bukkit.getPluginManager().getPlugin("UmbrellaOS"), () -> {
                        if (target.isOnline()) {
                            target.kickPlayer("\u00a7cRemoved for suspicious activity.\n\u00a77Check: " + checkName);
                        }
                    });
                }
            })
            .exceptionally(e -> { e.printStackTrace(); return null; });
        return true;
    }
}
