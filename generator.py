import pandas as pd
import numpy as np
import random

# Параметры
num_rows = 5000
np.random.seed(42)

# Возможные значения
protocols = ["ICMP", "UDP", "TCP"]
packet_types = ["Normal", "Malformed", "Fragmented"]
traffic_types = ["Normal", "Unusual", "Suspicious"]
attack_signatures = ["Sig_A", "Sig_B", "Sig_C"]
action_types = ["Allowed", "Blocked", "Quarantined"]
severity_levels = ["Low", "Medium", "High"]
log_sources = ["Firewall", "Endpoint", "IDS"]
attack_types = ["No_Attack", "Phishing", "Malware", "DDoS"]
network_segments = [f"Segment_{i}" for i in range(1, 11)]

# Генерация значений с корреляцией
malware_indicators = np.random.randint(0, 11, num_rows)

# Severity зависит от количества malware
severity_map = {i: "Low" if i <= 2 else "Medium" if i <= 5 else "High" for i in range(11)}
severity_levels_generated = [severity_map[i] for i in malware_indicators]

# Anomaly Score сильно зависит от количества malware + шум
anomaly_scores = np.clip(malware_indicators / 10 + np.random.normal(0, 0.05, num_rows), 0, 1)

# Alerts тоже коррелируют
alerts_warnings = np.clip(malware_indicators + np.random.randint(-2, 3, num_rows), 0, 10)
ids_ips_alerts = np.clip(malware_indicators + np.random.randint(-1, 2, num_rows), 0, 10)

# Генерация таблицы
data = {
    "Anomaly Scores": anomaly_scores,
    "Protocol": np.random.choice(protocols, num_rows),
    "Packet Type": np.random.choice(packet_types, num_rows),
    "Traffic Type": np.where(anomaly_scores > 0.7, "Suspicious",
                             np.where(anomaly_scores > 0.4, "Unusual", "Normal")),
    "Malware Indicators": malware_indicators,
    "Alerts/Warnings": alerts_warnings,
    "Attack Signature": np.random.choice(attack_signatures, num_rows),
    "Action Taken": np.where(anomaly_scores > 0.7, "Blocked",
                             np.where(anomaly_scores > 0.4, "Quarantined", "Allowed")),
    "Severity Level": severity_levels_generated,
    "Network Segment": np.random.choice(network_segments, num_rows),
    "Firewall Logs": np.random.randint(0, 11, num_rows),
    "IDS/IPS Alerts": ids_ips_alerts,
    "Log Source": np.random.choice(log_sources, num_rows),
    "Attack Type": np.where(malware_indicators > 7, "Malware",
                            np.where(anomaly_scores > 0.6, "DDoS",
                                     np.where(malware_indicators > 4, "Phishing", "None")))
}

# Сохранение
df = pd.DataFrame(data)
df.to_csv("correlated_network_data.csv", index=False)
print("Файл сохранён как correlated_network_data.csv")
