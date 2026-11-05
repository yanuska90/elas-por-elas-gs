"""Consulta somente a URL fixa do IBGE, com prazo, limite de tamanho e cache.

O cache reduz chamadas repetidas. Um snapshot público acompanha o projeto para
manter a seleção de municípios de SP disponível mesmo sem internet.
"""
import json
import threading
import time
from datetime import datetime, timezone
import requests
from .validacao import UFS, ErroValidacao

BASE_IBGE = 'https://servicodados.ibge.gov.br/api/v1/localidades/estados'


class FonteIndisponivel(Exception):
    pass


class Localidades:
    def __init__(self, config):
        self.config = config
        self.lock = threading.Lock()

    def consultar(self, uf):
        if uf not in UFS:
            raise ErroValidacao('UF inválida.')
        # O lock evita gravações simultâneas no mesmo arquivo de cache.
        with self.lock:
            return self._consultar(uf)

    def _consultar(self, uf):
        pasta = self.config['CACHE_DIR']
        pasta.mkdir(parents=True, exist_ok=True)
        destino = pasta / f'municipios_{uf}.json'
        salvo = None
        if destino.exists():
            try:
                salvo = json.loads(destino.read_text(encoding='utf-8'))
                if not isinstance(salvo.get('items'), list) or not salvo['items']:
                    salvo = None
                elif time.time() - destino.stat().st_mtime < self.config['CACHE_TTL_HOURS'] * 3600:
                    return dict(salvo, origem='cache', desatualizado=False)
            except (ValueError, OSError):
                salvo = None
        url = f'{BASE_IBGE}/{uf}/municipios'
        try:
            with requests.get(url, timeout=(3, 8), stream=True, allow_redirects=False,
                              headers={'User-Agent': 'ElasPorElasAcademico/1.0',
                                       'Accept': 'application/json'}) as resposta:
                resposta.raise_for_status()
                if resposta.status_code != 200:
                    raise ValueError('Resposta inesperada')
                conteudo = bytearray()
                for bloco in resposta.iter_content(32768):
                    conteudo.extend(bloco)
                    if len(conteudo) > 2_000_000:
                        raise ValueError('Resposta acima do limite')
                bruto = json.loads(conteudo)
            if not isinstance(bruto, list) or not 1 <= len(bruto) <= 6000:
                raise ValueError('Lista inválida')
            itens = []
            for item in bruto:
                if not isinstance(item, dict) or type(item.get('id')) is not int:
                    raise ValueError('Código inválido')
                nome = item.get('nome')
                if not isinstance(nome, str) or not 1 <= len(nome) <= 100:
                    raise ValueError('Nome inválido')
                if not 1_000_000 <= item['id'] <= 9_999_999 or '<' in nome or '>' in nome:
                    raise ValueError('Dados inválidos')
                itens.append({'id': item['id'], 'nome': nome, 'uf': uf})
            documento = {'source': url, 'uf': uf,
                         'consultado_em': datetime.now(timezone.utc).isoformat(), 'items': itens}
            # Gravação atômica: um arquivo parcial nunca substitui o cache válido.
            temporario = destino.with_suffix('.tmp')
            temporario.write_text(json.dumps(documento, ensure_ascii=False, indent=2), encoding='utf-8')
            temporario.replace(destino)
            return dict(documento, origem='api_ibge', desatualizado=False)
        except (requests.RequestException, ValueError, OSError, TypeError):
            if salvo:
                return dict(salvo, origem='cache', desatualizado=True)
            if uf == 'SP':
                snapshot = json.loads(self.config['SNAPSHOT'].read_text(encoding='utf-8'))
                return dict(snapshot, origem='snapshot_publico', desatualizado=True)
            raise FonteIndisponivel() from None
