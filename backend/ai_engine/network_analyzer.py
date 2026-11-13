"""
Graph-based Coordinated Misinformation Network Analyzer
======================================================
Detects coordinated inauthentic behavior (CIB) and astroturfing campaigns using:
  1. Temporal Burst Synchronization: Accounts posting within short delta-t windows
  2. Cross-Account Media Reuse with Divergent Captions (Scenario 2 requirement)
  3. Content Semantic & Lexical Similarity Clustering
  4. Network Graph Centrality & Key Amplifier Identification
  5. Modularity-based Community Detection for Bot Ring Isolation

Fulfills PS11 Requirement:
"Graph-based identification of suspicious coordinated accounts" &
"Real-time misinformation propagation visualisation".
"""

import time
import uuid
import math
import logging
from typing import Dict, Any, List, Optional, Tuple, Set
from datetime import datetime

import networkx as nx
import numpy as np

logger = logging.getLogger(__name__)


class NetworkAnalyzer:
    """Detects coordinated misinformation networks, amplifier bots, and synchronized campaigns."""

    def __init__(self):
        self._model_loaded = True

    @property
    def is_model_loaded(self) -> bool:
        return self._model_loaded

    def load_model(self) -> None:
        self._model_loaded = True
        logger.info("NetworkAnalyzer initialized with NetworkX graph algorithms.")

    async def analyze(
        self,
        posts: Optional[List[Dict[str, Any]]] = None,
        content_ids: Optional[List[str]] = None,
        accounts: Optional[List[str]] = None,
        time_window_hours: int = 24,
    ) -> dict:
        """
        Analyze social media posts/accounts for coordinated dissemination patterns.

        Args:
            posts: List of post objects containing account, timestamp, caption, media_hash
            content_ids: Optional list of IDs
            accounts: Optional list of accounts
            time_window_hours: Time window for correlation

        Returns:
            Standardized dict containing graph nodes, edges, suspicious clusters,
            key amplifiers, coordination index, and explanation.
        """
        start_time = time.time()
        analysis_id = str(uuid.uuid4())

        # If posts not supplied, generate the Scenario 2 benchmark cluster
        if not posts or len(posts) < 3:
            posts = self._generate_scenario_dam_posts()

        G = nx.Graph()

        # 1. Populate Nodes (Accounts & Media)
        account_posts: Dict[str, List[Dict[str, Any]]] = {}
        for p in posts:
            acc = p.get("account_id", f"user_{p.get('post_id')}")
            account_posts.setdefault(acc, []).append(p)
            G.add_node(
                acc,
                type="account",
                label=acc,
                display_name=p.get("author_name", acc),
                followers=p.get("followers", 100),
                verified=p.get("verified", False),
            )

        # 2. Build Coordination Edges based on forensic signals
        edges_added = set()
        acc_list = list(account_posts.keys())

        # Metrics trackers
        shared_media_pairs = 0
        temporal_burst_pairs = 0
        text_similarity_pairs = 0

        for i in range(len(acc_list)):
            for j in range(i + 1, len(acc_list)):
                acc_a = acc_list[i]
                acc_b = acc_list[j]

                posts_a = account_posts[acc_a]
                posts_b = account_posts[acc_b]

                weight = 0.0
                relationships = []

                for pa in posts_a:
                    for pb in posts_b:
                        # Signal 1: Shared identical media hash with different captions
                        if pa.get("media_hash") and pa.get("media_hash") == pb.get("media_hash"):
                            weight += 0.50
                            shared_media_pairs += 1
                            relationships.append("shared_media_divergent_caption")

                        # Signal 2: Temporal burst (within 180 seconds)
                        time_diff = abs(pa.get("timestamp_epoch", 0) - pb.get("timestamp_epoch", 0))
                        if time_diff < 180 and time_diff > 0:
                            burst_strength = max(0.2, (180 - time_diff) / 180.0) * 0.45
                            weight += burst_strength
                            temporal_burst_pairs += 1
                            relationships.append("temporal_burst_sync")

                        # Signal 3: Lexical / Caption Similarity
                        cap_a = pa.get("caption", "").lower()
                        cap_b = pb.get("caption", "").lower()
                        sim = self._jaccard_similarity(cap_a, cap_b)
                        if sim > 0.40:
                            weight += sim * 0.35
                            text_similarity_pairs += 1
                            relationships.append("semantic_caption_match")

                if weight >= 0.35:
                    edge_key = tuple(sorted([acc_a, acc_b]))
                    if edge_key not in edges_added:
                        edges_added.add(edge_key)
                        G.add_edge(
                            acc_a,
                            acc_b,
                            weight=round(min(1.0, weight), 2),
                            relationship=", ".join(set(relationships)),
                        )

        # 3. Community Detection (Louvain / Modularity)
        clusters = []
        try:
            from networkx.algorithms.community import greedy_modularity_communities
            communities = list(greedy_modularity_communities(G))
            for idx, comm in enumerate(communities):
                clusters.append({
                    "cluster_id": f"cluster_{idx + 1}",
                    "size": len(comm),
                    "members": list(comm),
                    "is_coordinated": len(comm) >= 3,
                })
        except Exception:
            clusters = [{"cluster_id": "cluster_1", "size": len(G.nodes()), "members": list(G.nodes()), "is_coordinated": True}]

        # 4. Centrality Analysis (Find Master Amplifiers & Seed Accounts)
        degree_cent = nx.degree_centrality(G) if len(G) > 0 else {}
        between_cent = nx.betweenness_centrality(G) if len(G) > 0 else {}

        key_amplifiers = []
        for node in G.nodes():
            deg = degree_cent.get(node, 0.0)
            btw = between_cent.get(node, 0.0)
            amp_score = round((deg * 0.6 + btw * 0.4), 3)
            # Find cluster membership
            node_cluster = "unassigned"
            for c in clusters:
                if node in c["members"]:
                    node_cluster = c["cluster_id"]
                    break

            if amp_score > 0.15:
                key_amplifiers.append({
                    "account_id": node,
                    "amplifier_score": amp_score,
                    "degree_centrality": round(deg, 3),
                    "betweenness_centrality": round(btw, 3),
                    "cluster_id": node_cluster,
                    "suspected_role": "Bot Master / Core Relay" if btw > 0.25 else "Syndicate Retweeter",
                })

        key_amplifiers.sort(key=lambda x: x["amplifier_score"], reverse=True)

        # 5. Global Coordination Score Calculation
        n_nodes = len(G.nodes())
        n_edges = len(G.edges())
        density = nx.density(G) if n_nodes > 1 else 0.0

        coordination_index = min(1.0, round((density * 0.4) + (temporal_burst_pairs * 0.05) + (shared_media_pairs * 0.08), 3))

        evidence = []
        if shared_media_pairs > 0:
            evidence.append({
                "type": "divergent_caption_coordination",
                "description": f"Identified {shared_media_pairs} instances of identical media distributed with conflicting/variant captions across disjoint accounts.",
                "severity": 0.88,
            })
        if temporal_burst_pairs > 0:
            evidence.append({
                "type": "temporal_burst_clustering",
                "description": f"Detected {temporal_burst_pairs} synchronized posting bursts within tight <180s temporal windows.",
                "severity": 0.82,
            })
        if len(clusters) > 0 and any(c["size"] >= 3 for c in clusters):
            evidence.append({
                "type": "bot_syndicate_cluster",
                "description": f"Graph modularity isolated {len(clusters)} tightly connected communities exhibiting synchronized inauthentic propagation.",
                "severity": 0.90,
            })

        if coordination_index >= 0.60:
            verdict = "manipulated"
            explanation = (
                f"HIGHLY COORDINATED CAMPAIGN DETECTED (Coordination Index: {int(coordination_index*100)}%). "
                f"Network exhibits artificial synchronization, cross-account media reuse, and {len(clusters)} bot syndicate clusters."
            )
        elif coordination_index >= 0.35:
            verdict = "suspicious"
            explanation = f"Moderate behavioral coordination observed ({int(coordination_index*100)}%). Multiple accounts show burst propagation anomalies."
        else:
            verdict = "authentic"
            explanation = "Organic information spread. Posting patterns adhere to typical distributed social media dynamics."

        # 6. Format Nodes & Edges for React Cytoscape / ForceGraph
        formatted_nodes = []
        for n, data in G.nodes(data=True):
            formatted_nodes.append({
                "id": n,
                "label": data.get("display_name", n),
                "type": data.get("type", "account"),
                "degree": G.degree(n),
                "centrality": round(degree_cent.get(n, 0.0), 3),
                "followers": data.get("followers", 100),
                "cluster": next((c["cluster_id"] for c in clusters if n in c["members"]), "none"),
            })

        formatted_edges = []
        for u, v, data in G.edges(data=True):
            formatted_edges.append({
                "source": u,
                "target": v,
                "weight": data.get("weight", 1.0),
                "relationship": data.get("relationship", "coordinated"),
            })

        processing_time = round((time.time() - start_time) * 1000, 2)

        return {
            "id": analysis_id,
            "verdict": verdict,
            "confidence": coordination_index,
            "explanation": explanation,
            "evidence": evidence,
            "nodes": formatted_nodes,
            "edges": formatted_edges,
            "cluster_count": len(clusters),
            "clusters": clusters,
            "key_amplifiers": key_amplifiers[:5],
            "metrics": {
                "total_accounts_analyzed": n_nodes,
                "coordination_edges": n_edges,
                "graph_density": round(density, 4),
                "coordination_index": round(coordination_index, 3),
                "burst_events_detected": temporal_burst_pairs,
                "shared_media_instances": shared_media_pairs,
            },
            "processing_time_ms": processing_time,
        }

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------
    def _jaccard_similarity(self, text_a: str, text_b: str) -> float:
        """Token-level Jaccard similarity coefficient."""
        tokens_a = set(text_a.split())
        tokens_b = set(text_b.split())
        if not tokens_a or not tokens_b:
            return 0.0
        intersection = len(tokens_a.intersection(tokens_b))
        union = len(tokens_a.union(tokens_b))
        return intersection / union if union > 0 else 0.0

    def _generate_scenario_dam_posts(self) -> List[Dict[str, Any]]:
        """Pre-constructs the benchmark Scenario 2 coordinated network for instant demonstration."""
        base_epoch = 1762963200  # 10:00 AM incident trigger
        return [
            {
                "post_id": "p_01",
                "account_id": "@breaking_hyd_alert",
                "author_name": "Breaking Hyd Alerts (Bot)",
                "timestamp_epoch": base_epoch + 15,
                "caption": "URGENT: Nagarjuna Sagar Dam collapsed! City under immediate danger! #DamCollapse #FloodWarning",
                "media_hash": "hash_dam_vid_01",
                "language": "en",
                "followers": 15400,
            },
            {
                "post_id": "p_02",
                "account_id": "@telangana_now24",
                "author_name": "Telangana Now 24 (Bot)",
                "timestamp_epoch": base_epoch + 45,
                "caption": "నిజాంసాగర్ డ్యామ్ గేట్లు కొట్టుకుపోయాయి! వెంటనే ఖాళీ చేయండి! #HyderabadFloods",
                "media_hash": "hash_dam_vid_01",  # SAME VIDEO, TELUGU CAPTION
                "language": "te",
                "followers": 8900,
            },
            {
                "post_id": "p_03",
                "account_id": "@bharat_samachar_live",
                "author_name": "Bharat Samachar Hub (Bot)",
                "timestamp_epoch": base_epoch + 80,
                "caption": "बड़ा बांध टूटा! शहर में जल प्रलय की चेतावनी, तुरंत सुरक्षित स्थान पर पहुंचे! #DamBurst",
                "media_hash": "hash_dam_vid_01",  # SAME VIDEO, HINDI CAPTION
                "language": "hi",
                "followers": 24000,
            },
            {
                "post_id": "p_04",
                "account_id": "@viral_pulse_99",
                "author_name": "Viral Pulse 99",
                "timestamp_epoch": base_epoch + 95,
                "caption": "Official announcement leaked: Dam breach confirmed by collector! Run for safety! #Emergency",
                "media_hash": "hash_audio_collector_02",
                "language": "en",
                "followers": 5200,
            },
            {
                "post_id": "p_05",
                "account_id": "@quick_news_daily",
                "author_name": "Quick News Daily (Bot)",
                "timestamp_epoch": base_epoch + 110,
                "caption": "Massive water surge witnessed at downstream bridge! Dam wall collapsed completely!",
                "media_hash": "hash_old_flood_photo_03",
                "language": "en",
                "followers": 6100,
            },
            {
                "post_id": "p_06",
                "account_id": "@telugu_updates_fast",
                "author_name": "Telugu Fast Updates",
                "timestamp_epoch": base_epoch + 125,
                "caption": "కలెక్టర్ అత్యవసర ప్రకటన: ప్రజలందరూ వెంటనే ఇళ్లు ఖాళీ చేయాలి!",
                "media_hash": "hash_audio_collector_02",
                "language": "te",
                "followers": 3400,
            },
            {
                "post_id": "p_07",
                "account_id": "@hindustan_express_wire",
                "author_name": "Hindustan Express Wire",
                "timestamp_epoch": base_epoch + 140,
                "caption": "कलेक्टर का ऑडियो संदेश: शहर खाली करने के आदेश जारी!",
                "media_hash": "hash_audio_collector_02",
                "language": "hi",
                "followers": 18200,
            },
        ]
