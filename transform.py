from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

def transformar_link(link_original):
    try:
        parsed = urlparse(link_original)
        params = parse_qs(parsed.query)
        params_clean = {k: v[0] if v else '' for k, v in params.items()}
        
        pa = params_clean.get('pa', '')
        transformado = False
        cambios = []
        
        # Regla 1: pa=38
        if pa == '38':
            if 'status' in params_clean and params_clean['status'] != 'c':
                params_clean['status'] = 'c'
                transformado = True
                cambios.append('status: t → c')
            if 'TermedQuotaID' in params_clean:
                del params_clean['TermedQuotaID']
                transformado = True
                cambios.append('Eliminado TermedQuotaID')
            if 'isc' in params_clean and params_clean['isc'] != '1000':
                params_clean['isc'] = '1000'
                transformado = True
                cambios.append('isc: 5104 → 1000')
        
        # Regla 2: pa=30
        elif pa == '30':
            if 'disposition' in params_clean and params_clean['disposition'] != '1':
                params_clean['disposition'] = '1'
                transformado = True
                cambios.append(f'disposition → 1')
            if 'status' in params_clean and params_clean['status'] != '1':
                params_clean['status'] = '1'
                transformado = True
                cambios.append(f'status → 1')
        
        # Regla 3: pa=43
        elif pa == '43':
            if 'status' in params_clean and params_clean['status'] != '1':
                params_clean['status'] = '1'
                transformado = True
                cambios.append(f'status → 1')
        
        # Regla 4: pa=16
        elif pa == '16':
            if 'status' in params_clean and params_clean['status'] != 'complete':
                params_clean['status'] = 'complete'
                transformado = True
                cambios.append(f'status → complete')
        
        # Regla 5: pa=41
        elif pa == '41':
            if 'status' in params_clean and params_clean['status'] == 't':
                params_clean['status'] = 'c'
                transformado = True
                cambios.append('status: t → c')
            elif 'status' in params_clean and params_clean['status'] != 'c':
                del params_clean['status']
                transformado = True
                cambios.append('Eliminado status no válido')
        
        # Regla 6: pa=29
        elif pa == '29':
            parametros_a_eliminar = [
                'redirect_status_position',
                'qualification_term_question_id',
                'qualification_term_question_key',
                'matched_qouta_id',
                'reason_id',
                'trans_id',
                'disqualify_reason'
            ]
            for param in parametros_a_eliminar:
                if param in params_clean:
                    del params_clean[param]
                    transformado = True
                    cambios.append(f'Eliminado {param}')
        
        # Regla 7: pa=11
        elif pa == '11':
            if 'status' in params_clean and params_clean['status'] == 'T':
                params_clean['status'] = 'S'
                transformado = True
                cambios.append('status: T → S')
            if 'id' in params_clean and params_clean['id'] == '44':
                params_clean['id'] = '10'
                transformado = True
                cambios.append('id: 44 → 10')
        
        # Regla 8: pa=7
        elif pa == '7':
            if 'status' in params_clean and params_clean['status'] == 'quality_terminate':
                params_clean['status'] = 'quality_complete'
                transformado = True
                cambios.append('status: quality_terminate → quality_complete')
        
        nueva_query = urlencode(params_clean, doseq=False)
        nueva_url = urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            nueva_query,
            parsed.fragment
        ))
        
        return {
            'original': link_original,
            'transformado': nueva_url,
            'success': transformado,
            'cambios': cambios,
            'pa': pa
        }
        
    except Exception as e:
        return {
            'error': str(e),
            'original': link_original,
            'transformado': link_original,
            'success': False,
            'cambios': [],
            'pa': 'error'
        }