#!/usr/bin/env python3
"""
Mode 5: Topic Evolution Timeline — Data Collector

Collects GitHub repos for a given topic across multiple search rounds,
outputting structured JSON for agent-driven domain classification and
D3.js timeline visualization.

Usage:
    python evolution_timeline.py "context engineering"
    python evolution_timeline.py "agent framework" --min-stars 50 --rounds 3
    python evolution_timeline.py "MCP" --output results.json

Architecture:
    This script handles DATA COLLECTION ONLY. The agent performs:
    - Scope boundary definition (Phase 1)
    - Domain classification using judgment cards (Phase 2-3)
    - Futurology analysis (Phase 6)
    - HTML report generation using templates/evolution-timeline.html
"""

import argparse
import json
import sys
import os
from datetime import datetime

# Add parent directory to path for gh_utils import
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gh_utils import run_gh, check_auth


def search_topic(topic, keywords=None, min_stars=20, max_results=200):
    """
    Search GitHub for repos matching a topic with multiple keyword variants.

    Args:
        topic: Primary search topic
        keywords: Additional keyword variants (list of strings)
        min_stars: Minimum star count filter
        max_results: Maximum results to return

    Returns:
        List of repo dicts with: name, stars, forks, description, language,
        created_at, updated_at, url, topics
    """
    all_keywords = [topic]
    if keywords:
        all_keywords.extend(keywords)

    seen = set()
    results = []

    for kw in all_keywords:
        query = f"{kw} stars:>={min_stars}"
        cmd = [
            "search", "repos", query,
            "--sort", "stars",
            "--order", "desc",
            "--limit", str(min(100, max_results)),
            "--json", "nameWithOwner,stargazerCount,forkCount,description,"
                      "primaryLanguage,createdAt,updatedAt,url,repositoryTopics"
        ]

        data = run_gh(cmd)
        if not data:
            continue

        repos = json.loads(data) if isinstance(data, str) else data
        for repo in repos:
            name = repo.get("nameWithOwner", "")
            if name in seen:
                continue
            seen.add(name)

            # Extract language name from nested object
            lang_obj = repo.get("primaryLanguage") or {}
            language = lang_obj.get("name", "") if isinstance(lang_obj, dict) else ""

            # Extract topic names from nested objects
            topics_raw = repo.get("repositoryTopics", []) or []
            topics = []
            for t in topics_raw:
                if isinstance(t, dict):
                    topic_node = t.get("topic", {})
                    if isinstance(topic_node, dict):
                        topics.append(topic_node.get("name", ""))
                    else:
                        topics.append(str(t.get("name", "")))
                else:
                    topics.append(str(t))

            results.append({
                "name": name,
                "stars": repo.get("stargazerCount", 0),
                "forks": repo.get("forkCount", 0),
                "description": (repo.get("description") or "")[:200],
                "language": language,
                "created_at": repo.get("createdAt", ""),
                "updated_at": repo.get("updatedAt", ""),
                "url": repo.get("url", f"https://github.com/{name}"),
                "topics": topics,
                "source_keyword": kw
            })

            if len(results) >= max_results:
                break

        if len(results) >= max_results:
            break

    # Sort by stars descending
    results.sort(key=lambda r: r["stars"], reverse=True)
    return results


def build_output(topic, results, round_num=1):
    """Build structured output for agent consumption."""
    # Year distribution
    year_dist = {}
    for r in results:
        created = r.get("created_at", "")
        if created:
            year = created[:4]
            year_dist[year] = year_dist.get(year, 0) + 1

    # Language distribution
    lang_dist = {}
    for r in results:
        lang = r.get("language", "") or "Unknown"
        lang_dist[lang] = lang_dist.get(lang, 0) + 1

    return {
        "meta": {
            "topic": topic,
            "search_round": round_num,
            "total_results": len(results),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "year_distribution": dict(sorted(year_dist.items())),
            "language_distribution": dict(
                sorted(lang_dist.items(), key=lambda x: x[1], reverse=True)[:10]
            )
        },
        "projects": results
    }


def main():
    parser = argparse.ArgumentParser(
        description="Mode 5: Collect GitHub repos for topic evolution timeline"
    )
    parser.add_argument("topic", help="Technical topic to map")
    parser.add_argument(
        "--also", nargs="*", default=[],
        help="Additional keyword variants"
    )
    parser.add_argument(
        "--min-stars", type=int, default=20,
        help="Minimum star count (default: 20)"
    )
    parser.add_argument(
        "--max-results", type=int, default=200,
        help="Maximum results per round (default: 200)"
    )
    parser.add_argument(
        "--round", type=int, default=1,
        help="Search round number (for progress tracking)"
    )
    parser.add_argument(
        "--output", type=str, default=None,
        help="Output file path (default: stdout as JSON)"
    )

    args = parser.parse_args()

    # Auth check
    if not check_auth():
        print(json.dumps({"error": "gh CLI not authenticated. Run: gh auth login"}))
        sys.exit(1)

    # Run search
    all_keywords = [args.topic] + args.also if args.also else None
    results = search_topic(
        args.topic,
        keywords=args.also if args.also else None,
        min_stars=args.min_stars,
        max_results=args.max_results
    )

    output = build_output(args.topic, results, args.round)

    # Output
    output_json = json.dumps(output, ensure_ascii=True, indent=2)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output_json)
        print(f"Saved {len(results)} results to {args.output}")
    else:
        print(output_json)


if __name__ == "__main__":
    main()
