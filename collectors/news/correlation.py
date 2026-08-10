from typing import List

class Correlator:
    def __init__(self, db_cursor):
        """
        Initializes the Correlator with an active database cursor.
        """
        self.cursor = db_cursor

    def correlate_cves(self, cves: List[str]) -> List[int]:
        """
        Checks if the extracted CVEs exist in the vulnerabilities table.
        Returns a list of matching internal vulnerability IDs.
        """
        if not cves:
            return []
            
        try:
            # Using PostgreSQL ANY() array syntax for efficient batch matching
            self.cursor.execute(
                "SELECT id FROM vulnerabilities WHERE cve_id = ANY(%s)",
                (cves,)
            )
            results = self.cursor.fetchall()
            return [r[0] for r in results]
        except Exception as e:
            # Rollback since the cursor is shared
            self.cursor.connection.rollback()
            raise e

    def correlate_indicators(self, iocs: List[str]) -> List[int]:
        """
        Checks if the extracted IOCs (IPs, Domains, Hashes, etc.) exist in the indicators table.
        Returns a list of matching internal indicator IDs.
        """
        if not iocs:
            return []
            
        try:
            self.cursor.execute(
                "SELECT id FROM indicators WHERE indicator_value = ANY(%s)",
                (iocs,)
            )
            results = self.cursor.fetchall()
            return [r[0] for r in results]
        except Exception as e:
            self.cursor.connection.rollback()
            raise e
