# Models - descomentar conforme implementar
# from app.models.customer import Customer
# from app.models.order import Order
# from app.models.student import Student
# from app.models.recovery import RecoveryLead

# Camada de prospeccao (docs/architecture/prospeccao-fanatica-schema.md)
# Substitui o interaction.py que nunca chegou a ser implementado.
from app.models.lead import Lead
from app.models.atividade import AtividadeProspeccao
from app.models.metrica_diaria import MetricaDiaria
from app.models.reuniao_venda import ReuniaoVenda
from app.models.referido import Referido
