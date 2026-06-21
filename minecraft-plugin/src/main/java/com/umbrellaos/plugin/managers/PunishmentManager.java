package com.umbrellaos.plugin.managers;

import com.umbrellaos.plugin.api.CoreApiClient;

import java.util.*;
import java.util.concurrent.CompletableFuture;
import java.time.OffsetDateTime;

public class PunishmentManager {
    private final CoreApiClient apiClient;
    private final Map<UUID, List<Map<String, Object>>> punishmentCache = new HashMap<>();

    public PunishmentManager(CoreApiClient apiClient) {
        this.apiClient = apiClient;
    }

    public void refresh(UUID uuid) {
        apiClient.getPunishments(uuid.toString()).thenAccept(punishments -> {
            punishmentCache.put(uuid, punishments);
        }).exceptionally(e -> {
            e.printStackTrace();
            return null;
        });
    }

    /**
     * Blocking version of refresh() — waits for the API response before
     * returning, so callers (e.g. the login check) can safely call
     * isBanned()/isMuted() immediately after with up-to-date data.
     */
    public void refreshSync(UUID uuid) {
        try {
            List<Map<String, Object>> punishments = apiClient.getPunishments(uuid.toString()).get();
            punishmentCache.put(uuid, punishments);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private boolean isExpired(Map<String, Object> punishment) {
        Object expiresAt = punishment.get("expires_at");
        if (expiresAt == null) return false;
        try {
            return OffsetDateTime.parse(expiresAt.toString()).isBefore(OffsetDateTime.now());
        } catch (Exception e) {
            return false;
        }
    }

    public boolean isBanned(UUID uuid) {
        List<Map<String, Object>> punishments = punishmentCache.get(uuid);
        if (punishments == null) {
            return false;
        }
        for (Map<String, Object> punishment : punishments) {
            String type = (String) punishment.get("type");
            Boolean active = (Boolean) punishment.get("active");
            if (("ban".equalsIgnoreCase(type) || "tempban".equalsIgnoreCase(type))
                    && Boolean.TRUE.equals(active) && !isExpired(punishment)) {
                return true;
            }
        }
        return false;
    }

    public boolean isMuted(UUID uuid) {
        List<Map<String, Object>> punishments = punishmentCache.get(uuid);
        if (punishments == null) {
            return false;
        }
        for (Map<String, Object> punishment : punishments) {
            String type = (String) punishment.get("type");
            Boolean active = (Boolean) punishment.get("active");
            if ("mute".equalsIgnoreCase(type) && Boolean.TRUE.equals(active) && !isExpired(punishment)) {
                return true;
            }
        }
        return false;
    }

    public String getBanReason(UUID uuid) {
        List<Map<String, Object>> punishments = punishmentCache.get(uuid);
        if (punishments == null) {
            return null;
        }
        for (Map<String, Object> punishment : punishments) {
            String type = (String) punishment.get("type");
            Boolean active = (Boolean) punishment.get("active");
            if (("ban".equalsIgnoreCase(type) || "tempban".equalsIgnoreCase(type)) && Boolean.TRUE.equals(active)) {
                return (String) punishment.get("reason");
            }
        }
        return null;
    }
}
