from aro.domain.shared.value_objects import Criticity


class CriticityPolicy:
    """Classifie un score numérique (0-100) en niveau de criticité."""

    _THRESHOLDS: dict[Criticity, int] = {
        Criticity.CRITICAL: 90,
        Criticity.HIGH: 75,
        Criticity.MEDIUM: 50,
    }

    def classify(self, score: int) -> Criticity:
        if score >= self._THRESHOLDS[Criticity.CRITICAL]:
            return Criticity.CRITICAL
        if score >= self._THRESHOLDS[Criticity.HIGH]:
            return Criticity.HIGH
        if score >= self._THRESHOLDS[Criticity.MEDIUM]:
            return Criticity.MEDIUM
        return Criticity.LOW
