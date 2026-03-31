"""
Run this once to create the ChainTrace schema and install queries in TigerGraph.
Usage: python scripts/setup_schema.py
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pyTigerGraph as tg
from dotenv import load_dotenv
load_dotenv()

conn = tg.TigerGraphConnection(
    host=os.getenv("TG_HOST"),
    username=os.getenv("TG_USERNAME"),
    password=os.getenv("TG_PASSWORD"),
)

print("Creating graph...")
conn.gsql(f'CREATE GRAPH {os.getenv("TG_GRAPH_NAME", "ChainTrace")}()')
conn.graphname = os.getenv("TG_GRAPH_NAME", "ChainTrace")

print("Creating schema...")
schema_gsql = """
USE GRAPH ChainTrace

CREATE VERTEX Wallet (
  PRIMARY_ID address STRING,
  risk_score   FLOAT DEFAULT 0,
  flagged      BOOL  DEFAULT FALSE,
  total_sent   FLOAT DEFAULT 0,
  total_received FLOAT DEFAULT 0,
  tx_count     INT   DEFAULT 0,
  pagerank     FLOAT DEFAULT 0
)

CREATE VERTEX Transaction (
  PRIMARY_ID tx_id    STRING,
  amount      FLOAT,
  currency    STRING DEFAULT "BTC",
  timestamp   STRING,
  suspicious  BOOL DEFAULT FALSE
)

CREATE VERTEX Exchange (
  PRIMARY_ID name    STRING,
  country     STRING,
  regulated   BOOL DEFAULT TRUE
)

CREATE VERTEX IP_Address (
  PRIMARY_ID ip      STRING,
  country     STRING,
  vpn_flag    BOOL DEFAULT FALSE
)

CREATE DIRECTED EDGE sends (
  FROM Wallet, TO Transaction,
  amount FLOAT
)

CREATE DIRECTED EDGE received_by (
  FROM Transaction, TO Wallet,
  amount FLOAT
)

CREATE DIRECTED EDGE connected_to (
  FROM Wallet, TO Exchange
)

CREATE DIRECTED EDGE accessed_from (
  FROM Wallet, TO IP_Address
)

CREATE GRAPH ChainTrace (
  Wallet, Transaction, Exchange, IP_Address,
  sends, received_by, connected_to, accessed_from
)
"""
conn.gsql(schema_gsql)

print("Installing queries...")
queries_gsql = """
USE GRAPH ChainTrace

CREATE QUERY get_wallet_network(VERTEX<Wallet> wallet_id, INT max_hops = 2) FOR GRAPH ChainTrace {
  SetAccum<VERTEX> @@visited;
  SetAccum<EDGE>   @@edges;
  OrAccum<BOOL>    @visited;

  start = {wallet_id};
  @@visited += wallet_id;

  FOREACH i IN RANGE[1, max_hops] DO
    next = SELECT t
      FROM start:s -(sends>|received_by>|connected_to>)- :t
      WHERE NOT t.@visited
      ACCUM t.@visited += TRUE,
            @@visited  += t,
            @@edges    += s-(sends>)-t,
            @@edges    += s-(received_by>)-t;
    start = next;
  END;

  wallets       = {Wallet.*}  WHERE wallets IN @@visited;
  transactions  = {Transaction.*} WHERE transactions IN @@visited;

  PRINT wallets AS wallets, transactions AS transactions, @@edges AS edges;
}

CREATE QUERY shortest_path(VERTEX<Wallet> source, VERTEX<Wallet> target) FOR GRAPH ChainTrace {
  SetAccum<VERTEX> @@path;
  MinAccum<INT>    @dist;
  MapAccum<VERTEX, VERTEX> @@prev;

  source.@dist = 0;
  current = {source};

  WHILE current.size() > 0 DO
    current = SELECT t
      FROM current:s -(sends>|received_by>)- :t
      WHERE t.@dist == GSQL_INT_MAX
      ACCUM t.@dist += s.@dist + 1,
            @@prev  += (t -> s);
    IF target.@dist < GSQL_INT_MAX THEN BREAK; END;
  END;

  v = target;
  WHILE v != source DO
    @@path += v;
    v = @@prev.get(v);
  END;
  @@path += source;

  PRINT @@path AS path;
}

CREATE QUERY community_detection() FOR GRAPH ChainTrace {
  MapAccum<VERTEX, INT> @@community_map;
  INT cid = 0;
  SetAccum<VERTEX> @@processed;

  all_wallets = {Wallet.*};

  all_wallets = SELECT w FROM all_wallets:w
    POST-ACCUM
      IF NOT w IN @@processed THEN
        @@community_map += (w -> cid),
        @@processed     += w,
        cid             += 1
      END;

  PRINT @@community_map;
}

CREATE QUERY pagerank(FLOAT damping = 0.85, INT max_iter = 20) FOR GRAPH ChainTrace {
  MaxAccum<FLOAT> @rank;
  SumAccum<FLOAT> @new_rank;
  SumAccum<INT>   @out_degree;
  HeapAccum<VERTEX<Wallet>>(20, @rank DESC) @@top_scores;

  all = {Wallet.*};

  all = SELECT w FROM all:w
    POST-ACCUM w.@rank = 1.0, w.@out_degree = w.outdegree("sends");

  FOREACH i IN RANGE[1, max_iter] DO
    all = SELECT t
      FROM all:s -(sends>)- :t
      ACCUM t.@new_rank += s.@rank / (s.@out_degree + 0.0001)
      POST-ACCUM t.@rank = (1 - damping) + damping * t.@new_rank,
                 t.@new_rank = 0;
  END;

  all = SELECT w FROM all:w
    POST-ACCUM @@top_scores += w,
               w.pagerank = w.@rank;

  PRINT @@top_scores;
}

CREATE QUERY detect_cycles(VERTEX<Wallet> start_wallet) FOR GRAPH ChainTrace {
  SetAccum<VERTEX>         @@cycle_vertices;
  ListAccum<ListAccum<VERTEX>> @@cycle_paths;
  SetAccum<VERTEX>         @visited;

  start = {start_wallet};

  path1 = SELECT t FROM start:s -(sends>)- Transaction:tx -(received_by>)- Wallet:t
    WHERE t == start_wallet
    ACCUM @@cycle_paths += [s, tx, t];

  path2 = SELECT t FROM start:s -(sends>)- Transaction:tx -(received_by>)- Wallet:mid
            -(sends>)- Transaction:tx2 -(received_by>)- Wallet:t
    WHERE t == start_wallet
    ACCUM @@cycle_paths += [s, tx, mid, tx2, t];

  PRINT @@cycle_paths AS cycle_paths;
}

CREATE QUERY compute_risk_scores() FOR GRAPH ChainTrace {
  SumAccum<FLOAT> @score;
  SumAccum<INT>   @flagged_neighbors;

  all = {Wallet.*};

  # Factor 1: flagged neighbor count
  all = SELECT t FROM all:s -(sends>)- Transaction -(received_by>)- Wallet:t
    WHERE s.flagged == TRUE
    ACCUM t.@flagged_neighbors += 1;

  # Factor 2: transaction volume
  all = SELECT w FROM all:w
    POST-ACCUM
      w.@score = (w.@flagged_neighbors * 20.0)
               + (w.pagerank * 30.0)
               + (w.tx_count > 100 ? 20.0 : w.tx_count * 0.2),
      w.risk_score = (w.@score > 100 ? 100 : w.@score);

  PRINT all;
}
"""
conn.gsql(queries_gsql)

print("Installing queries (compiling)...")
conn.gsql("""
USE GRAPH ChainTrace
INSTALL QUERY get_wallet_network, shortest_path, community_detection, pagerank, detect_cycles, compute_risk_scores
""")

print("✅ Schema and queries installed successfully!")
print(f"   Graph: {os.getenv('TG_GRAPH_NAME', 'ChainTrace')}")
print(f"   Host:  {os.getenv('TG_HOST')}")
