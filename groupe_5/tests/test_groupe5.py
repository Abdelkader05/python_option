#!/usr/bin/env python3
"""
Programme de vérification pour le Groupe 5 - Navigation et Recommandations.

Ce script teste:
- PARTIE COMMUNE: Connexion, CRUD de base
- PARTIE SPECIFIQUE: Filtrage, recommandations, prochain AAV

Usage:
    python test_groupe5.py
    python test_groupe5.py --url http://localhost:8000
"""

import argparse
import sys
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False
    import urllib.request
    import urllib.error
    import json


class TestStatus(Enum):
    """Statut d'un test."""
    PASSED = "✅ PASS"
    FAILED = "❌ FAIL"
    SKIPPED = "⏭️  SKIP"
    ERROR = "💥 ERR"


@dataclass
class TestResult:
    """Résultat d'un test."""
    name: str
    status: TestStatus
    message: str = ""
    details: Optional[Dict] = None


class BaseTester:
    """Classe de base pour les tests."""

    def __init__(self, base_url: str = "http://localhost:8000", verbose: bool = False):
        self.base_url = base_url.rstrip("/")
        self.verbose = verbose
        self.results: List[TestResult] = []
        self.client = None

        if HAS_HTTPX:
            self.client = httpx.Client(base_url=self.base_url, timeout=10.0)

    def log(self, message: str, level: str = "info"):
        """Affiche un message si verbose est activé."""
        if self.verbose or level in ["error", "success"]:
            prefix = {
                "info": "ℹ️  ",
                "success": "✅ ",
                "error": "❌ ",
                "warning": "⚠️  ",
                "test": "🧪 "
            }.get(level, "")
            print(f"{prefix}{message}")

    def _request(self, method: str, endpoint: str, **kwargs) -> tuple:
        """Effectue une requête HTTP."""
        url = f"{self.base_url}{endpoint}"
        try:
            if HAS_HTTPX and self.client:
                response = self.client.request(method, endpoint, **kwargs)
                return response.status_code, response.json() if response.content else None, None
            else:
                req = urllib.request.Request(
                    url,
                    data=kwargs.get('json', {}).encode() if 'json' in kwargs else None,
                    headers={'Content-Type': 'application/json'} if 'json' in kwargs else {},
                    method=method
                )
                with urllib.request.urlopen(req, timeout=10) as response:
                    status = response.status
                    data = json.loads(response.read().decode()) if response.read() else None
                    return status, data, None
        except Exception as e:
            return None, None, str(e)

    def add_result(self, name: str, status: TestStatus, message: str = "", details: Optional[Dict] = None):
        """Ajoute un résultat de test."""
        self.results.append(TestResult(name=name, status=status, message=message, details=details))

    # =============================================================================
    # PARTIE COMMUNE - Tests de base
    # =============================================================================

    def test_health_check(self):
        """Teste le endpoint /health."""
        self.log("Test: Health check", "test")
        status, data, error = self._request("GET", "/health")
        if error:
            self.add_result("Health Check", TestStatus.ERROR, f"Erreur: {error}")
            return False
        if status == 200 and data and data.get("status") == "healthy":
            self.add_result("Health Check", TestStatus.PASSED, "Serveur opérationnel")
            return True
        else:
            self.add_result("Health Check", TestStatus.FAILED, f"Status: {status}")
            return False

    def test_root_endpoint(self):
        """Teste le endpoint /."""
        self.log("Test: Root endpoint", "test")
        status, data, error = self._request("GET", "/")
        if error:
            self.add_result("Root Endpoint", TestStatus.ERROR, f"Erreur: {error}")
            return False
        if status == 200 and data and "PlatonAAV" in data.get("message", ""):
            self.add_result("Root Endpoint", TestStatus.PASSED, "API accessible")
            return True
        else:
            self.add_result("Root Endpoint", TestStatus.FAILED, f"Status: {status}")
            return False

    def test_list_aavs(self):
        """Teste GET /aavs/."""
        self.log("Test: Liste des AAV", "test")
        status, data, error = self._request("GET", "/aavs/")
        if error:
            self.add_result("List AAVs", TestStatus.ERROR, f"Erreur: {error}")
            return False
        if status == 200 and isinstance(data, list):
            self.add_result("List AAVs", TestStatus.PASSED, f"{len(data)} AAV récupérés")
            return True
        else:
            self.add_result("List AAVs", TestStatus.FAILED, f"Status: {status}")
            return False

    # =============================================================================
    # PARTIE SPECIFIQUE AU GROUPE 5
    # =============================================================================

    def test_filtrage_aavs(self):
        """Teste GET /apprenants/{id}/aavs/filtrer."""
        self.log("Test: Filtrage des AAV pour un apprenant", "test")
        status, data, error = self._request("GET", "/apprenants/1/aavs/filtrer")
        if error:
            self.add_result("Filtrage AAVs", TestStatus.ERROR, f"Erreur: {error}")
            return False
        if status == 200 and data and "accessible" in data:
            self.add_result("Filtrage AAVs", TestStatus.PASSED, "Filtrage réussi")
            return True
        elif status == 404:
            self.add_result("Filtrage AAVs", TestStatus.SKIPPED, "Endpoint non implémenté (Groupe 5)")
            return True
        else:
            self.add_result("Filtrage AAVs", TestStatus.FAILED, f"Status: {status}")
            return False

    def test_recommandation(self):
        """Teste GET /apprenants/{id}/recommandations."""
        self.log("Test: Recommandations pour l'apprenant", "test")
        status, data, error = self._request("GET", "/apprenants/1/recommandations")
        if error:
            self.add_result("Recommandations", TestStatus.ERROR, f"Erreur: {error}")
            return False
        if status == 200 and data and "prochain_aav_recommande" in data:
            self.add_result("Recommandations", TestStatus.PASSED, "Recommandations récupérées")
            return True
        elif status == 404:
            self.add_result("Recommandations", TestStatus.SKIPPED, "Endpoint non implémenté (Groupe 5)")
            return True
        else:
            self.add_result("Recommandations", TestStatus.FAILED, f"Status: {status}")
            return False

    def test_verifier_prerequis(self):
        """Teste GET /apprenants/{id}/aavs/{id}/verifier."""
        self.log("Test: Vérification des prérequis", "test")
        status, data, error = self._request("GET", "/apprenants/1/aavs/8/verifier")
        if error:
            self.add_result("Verifier Prerequis", TestStatus.ERROR, f"Erreur: {error}")
            return False
        if status == 200 and data and "accessibilite" in data:
            self.add_result("Verifier Prerequis", TestStatus.PASSED, f"Accessibilité: {data.get('accessibilite')}")
            return True
        elif status == 404:
            self.add_result("Verifier Prerequis", TestStatus.SKIPPED, "Endpoint non implémenté (Groupe 5)")
            return True
        else:
            self.add_result("Verifier Prerequis", TestStatus.FAILED, f"Status: {status}")
            return False

    def test_liste_aavs_accessibles(self):
        """Teste GET /apprenants/{id}/aavs/accessible."""
        self.log("Test: Liste des AAV accessibles", "test")
        status, data, error = self._request("GET", "/apprenants/1/aavs/accessible")
        if error:
            self.add_result("AAVs Accessibles", TestStatus.ERROR, f"Erreur: {error}")
            return False
        if status == 200 and isinstance(data, list):
            self.add_result("AAVs Accessibles", TestStatus.PASSED, f"{len(data)} AAVs accessibles")
            return True
        elif status == 404:
            self.add_result("AAVs Accessibles", TestStatus.SKIPPED, "Endpoint non implémenté (Groupe 5)")
            return True
        else:
            self.add_result("AAVs Accessibles", TestStatus.FAILED, f"Status: {status}")
            return False

    def run_all_tests(self):
        """Exécute tous les tests."""
        print("\n" + "=" * 70)
        print("  PLATONAAV - TESTS GROUPE 5 (Navigation et Recommandations)")
        print("=" * 70)
        print(f"\n🌐 URL: {self.base_url}")
        print(f"📦 Client: {'httpx' if HAS_HTTPX else 'urllib (fallback)'}")
        print()

        # Partie Commune
        print("-" * 70)
        print("🔌 PARTIE COMMUNE - Tests de base")
        print("-" * 70)
        self.test_root_endpoint()
        self.test_health_check()
        self.test_list_aavs()

        # Partie Spécifique
        print("\n" + "-" * 70)
        print("🧭 PARTIE SPECIFIQUE - Groupe 5 (Navigation et Recommandations)")
        print("-" * 70)
        self.test_filtrage_aavs()
        self.test_recommandation()
        self.test_verifier_prerequis()
        self.test_liste_aavs_accessibles()

        # Résumé
        self.print_summary()

    def print_summary(self):
        """Affiche le résumé des tests."""
        print("\n" + "=" * 70)
        print("  RÉSULTATS")
        print("=" * 70)

        passed = sum(1 for r in self.results if r.status == TestStatus.PASSED)
        failed = sum(1 for r in self.results if r.status == TestStatus.FAILED)
        errors = sum(1 for r in self.results if r.status == TestStatus.ERROR)
        skipped = sum(1 for r in self.results if r.status == TestStatus.SKIPPED)

        print(f"\n  ✅ Réussis:  {passed}")
        print(f"  ❌ Échoués: {failed}")
        print(f"  💥 Erreurs:  {errors}")
        print(f"  ⏭️  Ignorés: {skipped}")
        print(f"\n  📊 Total:    {len(self.results)} tests")

        if failed > 0 or errors > 0:
            print("\n" + "-" * 70)
            print("  DÉTAILS DES ÉCHECS")
            print("-" * 70)
            for result in self.results:
                if result.status in [TestStatus.FAILED, TestStatus.ERROR]:
                    print(f"\n  {result.name}")
                    print(f"     Status: {result.status.value}")
                    print(f"     Message: {result.message}")

        print("\n" + "=" * 70)
        return failed == 0 and errors == 0


def main():
    parser = argparse.ArgumentParser(description="Tests pour le Groupe 5 - Navigation et Recommandations")
    parser.add_argument("--url", default="http://localhost:8000", help="URL de l'API")
    parser.add_argument("--verbose", "-v", action="store_true", help="Mode verbeux")
    args = parser.parse_args()

    tester = BaseTester(base_url=args.url, verbose=args.verbose)
    tester.run_all_tests()


if __name__ == "__main__":
    main()
