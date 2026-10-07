"""Apply reviewed partner-catalog facts and correct extraction labels.

Run from the repository root. The gp number identifies a source record, not
a manufacturer SKU. Reviewed facts come from the supplier's product pages.
"""
import html
import json
import re
from pathlib import Path

FACTS = {
    3583: [('Material', 'Polipropileno (PP)'), ('Presentación', 'Bolsa de 1000 unidades'), ('Diseño', 'Puntera de ajuste cónico'), ('Esterilización publicada', 'Autoclave a 121 °C durante 20 minutos'), ('Compatibilidad', 'Confirmar volumen, modelo de micropipeta y ajuste antes de seleccionar')],
    5536: [('Serie', 'BH-250'), ('Tipo', 'Calentador de bloques secos intercambiables'), ('Recipientes', 'Tubos y placas de muestra; seleccionar bloques compatibles'), ('Indicadores independientes', 'Alimentación, calentamiento y desconexión por sobretemperatura'), ('Diseño', 'Unidades apilables cuando no se utilizan'), ('Configuración', 'Número de bloques según el modelo; confirmar al cotizar')],
    5590: [('Tipo', 'Bomba de vacío por efecto Venturi'), ('Alimentación', 'Aire comprimido; no requiere conexión eléctrica ni baterías'), ('Control', 'Interruptor neumático de nivel de vacío'), ('Ahorro de aire', 'Corta el suministro al alcanzar el vacío ajustado'), ('Retención de vacío', 'Mantiene el vacío ante la pérdida del suministro de aire')],
    5758: [('Tipo', 'Caudalímetro de área variable de un solo tubo'), ('Fluidos', 'Aire y agua'), ('Longitud de escala', '150 mm; escala universal Optigrad'), ('Racores', 'Acero inoxidable'), ('Válvula', 'Sin válvula'), ('Montaje', 'Panel con tuercas hexagonales; adaptador no giratorio'), ('Protección de lectura', 'Placas protectoras y lupa'), ('Rango de caudal', 'Depende del tubo y de las condiciones de presión y temperatura')],
    5772: [('Tipo', 'Caudalímetro de área variable de un solo tubo'), ('Fluidos', 'Aire y agua'), ('Longitud de escala', '150 mm; escala universal Optigrad'), ('Racores', 'Acero inoxidable'), ('Control de caudal', 'Válvula integrada de alta resolución'), ('Montaje', 'Panel con tuercas hexagonales; adaptador no giratorio'), ('Rango de caudal', 'Depende del tubo y de las condiciones de presión y temperatura')],
    5548: [('Serie', 'FSB-200 industrial'), ('Aplicación', 'Limpieza térmica de herramientas y piezas con residuos de polímeros'), ('Medio', 'Óxido de aluminio fluidizado'), ('Temperatura máxima publicada', '600 °C'), ('Control', 'PID digital con termopar tipo K'), ('Suministro requerido', 'Aire seco o gas inerte; nitrógeno o argón'), ('Regulación de gas', 'Caudalímetro en el panel frontal'), ('Accesorios opcionales', 'Cestas para piezas pequeñas')],
    5460: [('Modelo', 'V-200'), ('Alimentación', '100–240 V; cable con adaptador universal'), ('Modos', 'Por contacto y continuo'), ('Velocidad', 'Variable; rango numérico no publicado en la fuente'), ('Cabezal incluido', 'Copa para un tubo de ensayo'), ('Cabezales opcionales', 'Para otros tubos y microplacas; intercambio sin herramientas'), ('Entorno de uso publicado', 'Cámaras frigoríficas o incubadoras')],
    3580: [('Material', 'Acero'), ('Tipo', 'Mechero Bunsen de gas'), ('Regulación de gas', 'Válvula de aguja inferior'), ('Regulación de aire', 'Collarín giratorio'), ('Base', 'Pesada para estabilidad sobre la mesa'), ('Conexión', 'Entrada lateral estriada para manguera'), ('Gas compatible', 'GLP o gas natural según configuración; confirmar antes de seleccionar'), ('Aplicaciones', 'Calentamiento, flameado de instrumental y ensayos a la llama')],
    3576: [('Material', 'Vidrio borosilicato'), ('Capacidades publicadas', '250, 500 y 1000 mL'), ('Uniones', 'Juntas esmeriladas'), ('Condensador', 'Tipo Liebig con camisa de agua'), ('Cabezal', 'Entrada para termómetro'), ('Componentes publicados', 'Balón de destilación y recipiente recolector; confirmar configuración suministrada'), ('Aplicación', 'Separación de líquidos y recuperación de disolventes')],
    5586: [('Modelo', 'Air Cadet PRO'), ('Tipo', 'Bomba de diafragma de uso general'), ('Vacío máximo publicado', '29,8 inHg'), ('Nivel sonoro publicado', '45 dB(A)'), ('Aplicaciones', 'Filtración y secado al vacío'), ('Variantes', 'Con lastre de gas para purgar contaminantes condensables; confirmar versión')],
    5588: [('Referencia anterior', 'RE3022C'), ('Tipo', 'Bomba de vacío de diafragma sin aceite'), ('Materiales publicados', 'PTFE y FFKM'), ('Control', 'Regulador de vacío con manómetro y perilla de ajuste'), ('Protección', 'Recipientes de recogida para impedir la entrada de líquidos'), ('Aplicación', 'Laboratorios químicos y evaporación rotatoria'), ('Incluye', 'Fuente de alimentación; confirmar tensión al cotizar')],
    5572: [('Serie', 'VP-200'), ('Tipo', 'Bomba de vacío/presión de cabezal único'), ('Motor', 'Sin escobillas; rodamientos sellados'), ('Cabezal', 'Noryl'), ('Diafragma', 'FKM'), ('Válvulas', 'PTFE'), ('Adaptadores', 'Polietileno (PE)')],
    5600: [('Cuerpo', 'Polipropileno (PP)'), ('Tapa', 'Policarbonato (PC)'), ('Junta', 'Neopreno'), ('Placa interna', 'Polipropileno rígido perforado'), ('Espacio inferior', 'Para desecante'), ('Aplicación', 'Secado y almacenamiento protegido de la humedad')],
    5618: [('Serie', 'WS-100'), ('Caldera y condensador', 'Vidrio borosilicato'), ('Agua de alimentación', 'Agua del grifo'), ('Protección', 'Dos termostatos independientes contra sobrecalentamiento'), ('Montaje', 'Pared o banco; soporte metálico incluido'), ('Conexiones del condensador', 'Roscadas con racores para manguera de 3/8 pulgadas de diámetro interior'), ('Aplicación', 'Destilación de agua para laboratorio y enseñanza')],
    5680: [('Tipo', 'Agitador magnético portátil a pilas'), ('Velocidad máxima publicada', '700 rpm'), ('Control', 'Ajuste continuo de velocidad'), ('Carcasa', 'Metal con revestimiento epoxi'), ('Superficie superior', 'Goma antideslizante'), ('Apoyo', 'Cuatro patas de goma'), ('Entorno de uso publicado', 'Incubadoras, campanas de extracción y cajas de guantes')],
    5530: [('Serie', 'CBH-400'), ('Tipo', 'Baño circulante con calefacción y refrigeración'), ('Rango de temperatura publicado', '−10 a 80 °C'), ('Control', 'Termostático'), ('Diseño', 'Compacto; tanque cerrado para reducir evaporación'), ('Aplicaciones', 'Instrumentación analítica, reactores con camisa y evaporadores rotatorios de baja carga')],
    5638: [('Serie', 'HP-200'), ('Control', 'Microprocesador y termopares duales'), ('Ajuste', 'Botones y dial'), ('Advertencia de placa caliente', 'Por encima de 50 °C; activa tras apagar mientras permanezca conectada'), ('Protección', 'Circuito independiente contra sobrecalentamiento'), ('Electrónica', 'Protegida contra corrosión'), ('Tratamiento superficial', 'BioCote')],
    5670: [('Serie', 'HP-300'), ('Tipo', 'Placa calefactora digital'), ('Pantalla', 'LED de 7 segmentos; temperatura programada y real'), ('Advertencia de superficie caliente', 'Por encima de 50 °C; permanece activa incluso tras desconectar'), ('Panel frontal', 'Resistente a derrames y productos químicos'), ('Tratamiento superficial', 'BioCote'), ('Opcional', 'Controlador digital de temperatura de la muestra')],
    5672: [('Serie', 'HP-300 redonda'), ('Superficie', 'Aluminio con revestimiento cerámico'), ('Pantalla', 'LCD; temperatura programada y real'), ('Control', 'Panel táctil utilizable con guantes'), ('Temporizador', 'Dos modos'), ('Bloqueo', 'Bloqueo de ajustes para evitar cambios accidentales'), ('Protección', 'Carcasa sellada y advertencia de temperatura alta')],
    5560: [('Modelo', 'GP'), ('Velocidad publicada', '40–4000 rpm'), ('Par máximo publicado', '6,7 N·cm'), ('Motor', 'Corriente continua con escobillas'), ('Protección', 'IP44 según IEC 60529; sobrecarga y bloqueo de rotor'), ('Control', 'Arranque suave y compensación electrónica de velocidad'), ('Portabrocas', 'Sin llave'), ('Aplicación', 'Mezcla ligera de fluidos similares al agua')],
    5562: [('Modelo', 'SP'), ('Velocidad publicada', '50–2500 rpm'), ('Par máximo publicado', '64 N·cm'), ('Motor', 'Sin escobillas'), ('Inclinación', 'Ajustable de 0 a 30°'), ('Protección', 'IP44 según IEC 60529; bloqueo de rotor y cortocircuitos'), ('Control', 'Arranque suave y compensación electrónica de velocidad'), ('Sujeción', 'Eje hueco pasante y mandril sin llave')],
    5750: [('Tipo', 'Caudalímetro de agua de área variable'), ('Cuerpo', 'Acrílico transparente'), ('Racores', 'Latón'), ('Control de caudal', 'Válvula integrada'), ('Escalas', 'Unidades inglesas o métricas según variante'), ('Montaje', 'Panel o en línea según configuración'), ('Mantenimiento', 'Desmontable para limpieza')],
    5768: [('Tipo', 'Caudalímetro de aire de área variable'), ('Cuerpo', 'Acrílico transparente'), ('Racores', 'Latón'), ('Válvula', 'Sin válvula'), ('Escalas', 'Unidades inglesas o métricas según variante'), ('Montaje', 'Panel o en línea según configuración'), ('Mantenimiento', 'Desmontable para limpieza')],
}

ROW = re.compile(r'<tr><td>([^<]*)</td><td>([^<]*)</td></tr>')
TABLE = re.compile(r'(<table class="spec-table" aria-label="Características y configuraciones"><tbody>)(.*?)(</tbody></table>)', re.S)

def refine_label(key, value):
    if key == 'Temperatura citada' and not re.search(r'[°º℃˚]', value):
        for pattern, label in [(r'\b(?:mm|cm)\b', 'Dimensión citada'), (r'\brpm\b', 'Velocidad citada'), (r'\b(?:minutos|segundos)\b', 'Tiempo citado'), (r'\bvatios\b', 'Potencia citada')]:
            if re.search(pattern, value):
                return label, value
    if key == 'Dimensión citada' and 'L/min' in value:
        return 'Dimensión y caudal citados', value
    return key, value

def main():
    changed = []
    for path in sorted(Path('productos').glob('gp-*.html')):
        source_id = int(path.name.split('-')[1])
        original = path.read_text()
        match = TABLE.search(original)
        if not match:
            continue
        old_facts = [(html.unescape(k), html.unescape(v)) for k, v in ROW.findall(match[2])]
        facts = FACTS.get(source_id)
        if facts is None:
            facts = []
            for key, value in old_facts:
                key, value = refine_label(key, value)
                if source_id == 5524 and key == 'Temperatura de autoclave':
                    key = 'Temperatura máxima de calentamiento publicada'
                if (key, value) not in facts:
                    facts.append((key, value))
            # Remove only exact duplicate values in generic extraction rows.
            generic = {'Valor citado', 'Características mencionadas', 'Temperatura citada', 'Velocidad citada', 'Protección mencionada', 'Conexiones mencionadas'}
            specific_values = {v.casefold().strip().rstrip('.') for k, v in facts if k not in generic}
            facts = [(k, v) for k, v in facts if not (k in generic and v.casefold().strip().rstrip('.') in specific_values)]
        if facts == old_facts:
            continue
        rows = ''.join('<tr><td>' + html.escape(k) + '</td><td>' + html.escape(v) + '</td></tr>' for k, v in facts)
        revised = original[:match.start(2)] + rows + original[match.end(2):]
        def schema_update(m):
            obj = json.loads(m[2])
            if obj.get('@type') == 'Product':
                obj['additionalProperty'] = [{'@type': 'PropertyValue', 'name': k, 'value': v} for k, v in facts]
            return m[1] + json.dumps(obj, ensure_ascii=False) + m[3]
        revised = re.sub(r'(<script type="application/ld\+json">)(.*?)(</script>)', schema_update, revised, flags=re.S)
        path.write_text(revised)
        changed.append(path.name)
    print(json.dumps({'changed': len(changed), 'files': changed}, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
