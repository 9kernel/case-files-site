#!/usr/bin/env node
// test-validate.mjs — testa CADA regra de rejeição do validate.mjs.
// Uso:  node scripts/test-validate.mjs
// Exit 1 se qualquer caso falhar. Roda no CI junto do validador.

import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { validateData } from './validate.mjs';

const tmpRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'validate-test-'));
const dataDir = path.join(tmpRoot, 'data');
fs.mkdirSync(path.join(dataDir, 'threads'), { recursive: true });

const participants = [
  { id: 'p-ana', name: 'Ana', role: 'r', aliases: [], summary: 's' },
  { id: 'p-bruno', name: 'Bruno', role: 'r', aliases: [], summary: 's' },
];

function msg(over = {}) {
  return {
    id: 'm-00001',
    date: '2024-03-11',
    time: '08:00',
    timestamp_precision: 'minute',
    sender_id: 'p-ana',
    content_kind: 'verbatim',
    content: 'primeira mensagem',
    editorial_note: null,
    verification: {
      level: 'secondary_source',
      origin: 'PF extraction',
      authority: null,
      court: null,
      case: null,
      document: null,
      page: null,
      figure: null,
      official_url: null,
      primary_document_located: false,
      verified_at: '2026-10-06',
    },
    sources: {
      primary: null,
      secondary: [{ publication: 'Veículo Teste', date: '2026-10-01', url: 'https://example.org/materia' }],
    },
    source_ref: 'Veículo Teste, 01/10/2026',
    added_in: 'abc1234',
    ...over,
  };
}

function officialMsg(over = {}) {
  return msg({
    id: 'm-00002',
    content_kind: 'verbatim_excerpt',
    content: 'trecho da mensagem',
    verification: {
      level: 'official_document',
      origin: 'PF extraction',
      authority: 'Polícia Federal',
      court: 'STF',
      case: 'PET 16662',
      document: 'IPJ-A nº 3298613/2026',
      page: 143,
      figure: 142,
      official_url: null,
      primary_document_located: true,
      verified_at: '2026-10-06',
    },
    sources: {
      primary: {
        type: 'official_document',
        authority: 'Polícia Federal',
        court: 'STF',
        case: 'PET 16662',
        document: 'IPJ-A nº 3298613/2026',
        page: 143,
        figure: 142,
        url: null,
      },
      secondary: [{ publication: 'R7', date: '2026-09-01', url: 'https://example.org/r7' }],
    },
    source_ref: 'PF · IPJ-A nº 3298613/2026 · fl. 143',
    ...over,
  });
}

function baseThread() {
  return {
    id: 'thread-teste',
    title: 'Thread de teste',
    participants_ids: ['p-ana', 'p-bruno'],
    source: { document: 'Documento da fonte', url: 'https://example.org/x', pages: 'reportagem única' },
    messages: [
      { ...msg(), date: '2024-03-11', time: '08:00', id: 'm-00001' },
      { ...officialMsg(), date: '2024-03-11', time: '08:05', id: 'm-00002' },
    ],
    timeline_events: [
      {
        id: 'e-00001',
        date: '2024-03-10',
        time: null,
        timestamp_precision: 'date',
        content: 'Evento editorial de contexto.',
        event_kind: 'editorial_context',
        verification: { level: 'secondary_source', origin: 'PF extraction', primary_document_located: false, verified_at: null },
        source_ref: 'Veículo Teste, 01/10/2026',
        added_in: 'abc1234',
      },
    ],
  };
}

function writeData(thread, participantsData = participants) {
  fs.writeFileSync(path.join(dataDir, 'participants.json'), JSON.stringify(participantsData));
  fs.writeFileSync(path.join(dataDir, 'threads', 'thread-teste.json'), JSON.stringify(thread));
}

function runCase(name, mutate, expectedCodes) {
  const thread = baseThread();
  mutate(thread);
  writeData(thread);
  const { errors } = validateData(dataDir, tmpRoot);
  const codes = new Set(errors.map((e) => e.code));
  const missing = expectedCodes.filter((c) => !codes.has(c));
  if (missing.length) {
    console.error(`✗ ${name}: esperava ${expectedCodes.join(', ')}, obtive ${[...codes].join(', ') || '(nenhum erro)'}`);
    for (const e of errors) console.error(`    ${e.code}: ${e.message}`);
    return false;
  }
  console.log(`✓ ${name} → ${expectedCodes.join(', ')}`);
  return true;
}

let ok = true;

/* caso-base DEVE passar sem erros (fonte válida + mensagem oficial completa) */
writeData(baseThread());
{
  const { errors, warnings } = validateData(dataDir, tmpRoot);
  if (errors.length) {
    console.error(`✗ caso-base deveria passar, mas gerou: ${errors.map((e) => `${e.code}: ${e.message}`).join('; ')}`);
    ok = false;
  } else {
    console.log(`✓ caso-base passa sem erros (${warnings.length} warning(s))`);
  }
}

/* cada regra de rejeição */
ok = runCase('sem source_ref', (t) => delete t.messages[0].source_ref, ['E_MISSING_SOURCE_REF']) && ok;
ok = runCase('source_ref vazio', (t) => { t.messages[0].source_ref = '  '; }, ['E_MISSING_SOURCE_REF']) && ok;
ok = runCase('sem sender', (t) => delete t.messages[0].sender_id, ['E_MISSING_SENDER']) && ok;
ok = runCase('sender inexistente', (t) => { t.messages[0].sender_id = 'p-fantasma'; }, ['E_UNKNOWN_SENDER']) && ok;
ok = runCase('evento editorial com sender_id', (t) => { t.messages[0].content_kind = 'editorial_event'; }, ['E_EVENT_SENDER']) && ok;
ok = runCase('evento da timeline com sender_id', (t) => { t.timeline_events[0].sender_id = 'p-ana'; }, ['E_EVENT_SENDER']) && ok;
ok = runCase('sem verification', (t) => delete t.messages[0].verification, ['E_MISSING_VERIFICATION']) && ok;
ok = runCase('nível de verificação inválido', (t) => { t.messages[0].verification = { ...t.messages[0].verification, level: 'confirmed' }; }, ['E_BAD_VERIFICATION_LEVEL']) && ok;
ok = runCase('official_document sem página', (t) => { t.messages[1].verification = { ...t.messages[1].verification, page: null }; }, ['E_VERIFICATION_SHAPE']) && ok;
ok = runCase('official_document sem documento', (t) => { t.messages[1].verification = { ...t.messages[1].verification, document: null }; }, ['E_VERIFICATION_SHAPE']) && ok;
ok = runCase('official_document sem authority', (t) => { t.messages[1].verification = { ...t.messages[1].verification, authority: null }; }, ['E_VERIFICATION_SHAPE']) && ok;
ok = runCase('official_document com primary_document_located=false', (t) => { t.messages[1].verification = { ...t.messages[1].verification, primary_document_located: false }; }, ['E_VERIFICATION_SHAPE']) && ok;
ok = runCase('official_document sem sources.primary', (t) => { t.messages[1].sources = { primary: null, secondary: [] }; }, ['E_VERIFICATION_SHAPE']) && ok;
ok = runCase('secondary_source sem fonte secundária', (t) => { t.messages[0].sources = { primary: null, secondary: [] }; }, ['E_VERIFICATION_SECONDARY']) && ok;
ok = runCase('secondary_source com fonte inválida', (t) => { t.messages[0].sources = { primary: null, secondary: [{ date: '2026-10-01' }] }; }, ['E_VERIFICATION_SECONDARY']) && ok;
ok = runCase('nível != official_document com primary_document_located=true', (t) => { t.messages[0].verification = { ...t.messages[0].verification, primary_document_located: true }; }, ['E_VERIFICATION_SHAPE']) && ok;
ok = runCase('datas fora de ordem', (t) => { t.messages[1].date = '2024-03-10'; }, ['E_TIMESTAMP_ORDER']) && ok;
ok = runCase('horas fora de ordem no mesmo dia', (t) => { t.messages[1].time = '07:00'; }, ['E_TIMESTAMP_ORDER']) && ok;
ok = runCase('mesmo dia com hora ausente NÃO compara ordem', (t) => {
  t.messages[1].date = '2024-03-11'; t.messages[1].time = null; t.messages[1].timestamp_precision = 'date';
}, []) && ok;
ok = runCase('date inválida', (t) => { t.messages[0].date = '11/03/2024'; }, ['E_BAD_DATE']) && ok;
ok = runCase('date inexistente (31/02)', (t) => { t.messages[0].date = '2024-02-31'; }, ['E_BAD_DATE']) && ok;
ok = runCase('time fora de HH:MM', (t) => { t.messages[0].time = '8h00'; }, ['E_BAD_TIME']) && ok;
ok = runCase('time impossível', (t) => { t.messages[0].time = '25:99'; }, ['E_BAD_TIME']) && ok;
ok = runCase('precisão inválida', (t) => { t.messages[0].timestamp_precision = 'second'; }, ['E_BAD_PRECISION']) && ok;
ok = runCase('precision=date com hora inventada', (t) => { t.messages[0].time = '12:00'; t.messages[0].timestamp_precision = 'date'; }, ['E_TIME_PRECISION_MISMATCH']) && ok;
ok = runCase('precision=minute sem hora', (t) => { t.messages[0].time = null; }, ['E_TIME_PRECISION_MISMATCH']) && ok;
ok = runCase('precision=month aceita YYYY-MM', (t) => { t.messages[0].date = '2024-03'; t.messages[0].time = null; t.messages[0].timestamp_precision = 'month'; }, []) && ok;
ok = runCase('id duplicado', (t) => { t.messages[1].id = 'm-00001'; }, ['E_DUPLICATE_ID']) && ok;
ok = runCase('id fora do padrão', (t) => { t.messages[0].id = 'msg1'; }, ['E_BAD_ID']) && ok;
ok = runCase('sem id', (t) => delete t.messages[0].id, ['E_MISSING_ID']) && ok;
ok = runCase('content_kind fora da lista', (t) => { t.messages[0].content_kind = 'palpite'; }, ['E_BAD_CONTENT_KIND']) && ok;
ok = runCase('sem content_kind', (t) => delete t.messages[0].content_kind, ['E_BAD_CONTENT_KIND']) && ok;
ok = runCase('áudio sem transcription_complete', (t) => { t.messages[0].content_kind = 'audio_transcript'; }, ['E_AUDIO_NEEDS_FLAGS']) && ok;
ok = runCase('áudio com transcription_complete passa', (t) => { t.messages[0].content_kind = 'audio_transcript'; t.messages[0].transcription_complete = false; }, []) && ok;
ok = runCase('verbatim com [texto editorial]', (t) => { t.messages[0].content = 'falando [pedindo desculpas] algo'; }, ['E_EDITORIAL_BRACKETS']) && ok;
ok = runCase('verbatim_excerpt com [colchetes] também é rejeitado', (t) => { t.messages[0].content = 'trecho [nota] da mensagem'; t.messages[0].content_kind = 'verbatim_excerpt'; }, ['E_EDITORIAL_BRACKETS']) && ok;
ok = runCase('literal_brackets: true libera colchetes do original', (t) => { t.messages[0].content = 'vote [sim] ontem'; t.messages[0].literal_brackets = true; }, []) && ok;
ok = runCase('áudio transcrito com colchetes passa (completição de transcrição)', (t) => {
  t.messages[0].content_kind = 'audio_transcript';
  t.messages[0].transcription_complete = false;
  t.messages[0].content = 'obrigado [inaudível] irmão';
}, []) && ok;
ok = runCase('sem added_in', (t) => delete t.messages[0].added_in, ['E_MISSING_ADDED_IN']) && ok;
ok = runCase('content não-string', (t) => { t.messages[0].content = 42; }, ['E_BAD_CONTENT']) && ok;
ok = runCase('reply_to inexistente', (t) => { t.messages[1].reply_to = 'm-99999'; }, ['E_BAD_REPLY_TO']) && ok;
ok = runCase('sender de thread inexistente em participants', (t) => { t.participants_ids = ['p-fantasma']; }, ['E_UNKNOWN_PARTICIPANT']) && ok;
ok = runCase('thread sem source', (t) => delete t.source, ['E_THREAD_FIELD']) && ok;
ok = runCase('media.url sem arquivo', (t) => { t.messages[0].content_kind = 'media'; t.messages[0].media = { kind: 'image', url: '/public/media/inexistente.png', filename: 'x.png' }; }, ['E_MISSING_MEDIA_FILE']) && ok;
ok = runCase('campo legado timestamp', (t) => { t.messages[0].timestamp = '2024-03-11T08:00:00-03:00'; }, ['E_LEGACY_FIELD']) && ok;
ok = runCase('campo legado status', (t) => { t.messages[0].status = 'confirmed'; }, ['E_LEGACY_FIELD']) && ok;
ok = runCase('campo legado type', (t) => { t.messages[0].type = 'text'; }, ['E_LEGACY_FIELD']) && ok;
ok = runCase('evento com id fora do padrão', (t) => { t.timeline_events[0].id = 'evento-1'; }, ['E_BAD_EVENT_ID']) && ok;
ok = runCase('evento com event_kind inválido', (t) => { t.timeline_events[0].event_kind = 'palpite'; }, ['E_BAD_EVENT_KIND']) && ok;
ok = runCase('evento com content vazio', (t) => { t.timeline_events[0].content = '  '; }, ['E_BAD_CONTENT']) && ok;

/* mídia: cadeia de proveniência (§35) */
const media = (over = {}) => ({ status: 'media_reference_only', ...over });
ok = runCase('official_media sem fonte oficial', (t) => {
  t.messages[0].media = media({ status: 'official_media', local_file: 'public/media/original/a.ogg', sha256: 'a'.repeat(64), bytes: 10 });
}, ['E_MEDIA_OFFICIAL']) && ok;
ok = runCase('official_media sem hash/arquivo', (t) => {
  t.messages[0].media = media({ status: 'official_media', source_document_id: 'pf-ipja-3298613-2026' });
}, ['E_MEDIA_OFFICIAL']) && ok;
ok = runCase('official_media com publisher jornalístico', (t) => {
  t.messages[0].media = media({ status: 'official_media', publisher: 'Poder360', local_file: 'public/media/original/a.ogg', sha256: 'a'.repeat(64), bytes: 10, source_authority: 'STF', source_process: 'INQ 5070' });
}, ['E_MEDIA_OFFICIAL']) && ok;
ok = runCase('official_media válido passa', (t) => {
  t.messages[0].media = media({ status: 'official_media', id: 'media-1', type: 'audio', local_file: 'public/media/original/a.ogg', sha256: 'a'.repeat(64), bytes: 10, source_document_id: 'stf-inq-5070' });
}, []) && ok;
ok = runCase('secondary_media sem publisher', (t) => {
  t.messages[0].media = media({ status: 'secondary_media', external_url: 'https://exemplo.org/audio' });
}, ['E_MEDIA_SECONDARY']) && ok;
ok = runCase('transcript_only com arquivo local', (t) => {
  t.messages[0].media = media({ status: 'transcript_only', local_file: 'public/media/a.ogg' });
}, ['E_MEDIA_TRANSCRIPT_ONLY']) && ok;
ok = runCase('transcript_only sem transcrição (mídia ausente não apaga o texto)', (t) => {
  t.messages[0].content = '';
  t.messages[0].media = media({ status: 'transcript_only' });
}, ['E_MEDIA_TRANSCRIPT_ONLY']) && ok;
ok = runCase('mídia local sem sha256', (t) => {
  t.messages[0].media = media({ status: 'media_reference_only', local_file: 'public/media/a.ogg', bytes: 10 });
}, ['E_MEDIA_LOCAL_HASH', 'E_MEDIA_REFERENCE']) && ok;
ok = runCase('mídia derivada sem derived_from', (t) => {
  t.messages[0].media = media({ status: 'media_reference_only', local_file: 'public/media/derived/a.mp3', sha256: 'a'.repeat(64), bytes: 10 });
}, ['E_MEDIA_DERIVED', 'E_MEDIA_REFERENCE']) && ok;
ok = runCase('original_file=true sem evidência documental', (t) => {
  t.messages[0].media = media({ original_file: true });
}, ['E_MEDIA_ORIGINAL_FILE']) && ok;
ok = runCase('áudio transcrito sem registro de mídia', (t) => {
  t.messages[0].content_kind = 'audio_transcript';
  t.messages[0].transcription_complete = false;
}, ['E_MEDIA_MISSING']) && ok;
ok = runCase('áudio com media id passa', (t) => {
  t.messages[0].content_kind = 'audio_transcript';
  t.messages[0].transcription_complete = false;
  t.messages[0].media = media({ status: 'transcript_only', id: 'media-audio-1' });
}, []) && ok;
ok = runCase('secondary_media válido (áudio do Intercept) passa', (t) => {
  t.messages[0].content_kind = 'media';
  t.messages[0].media = media({
    status: 'secondary_media', id: 'media-audio-2', type: 'audio',
    publisher: 'The Intercept Brasil', external_url: 'https://www.intercept.com.br/2026/05/19/audio-mario-frias-daniel-vorcaro/',
    official_media_located: false, original_file: false, media_representation: 'publisher_reproduction',
  });
}, []) && ok;

/* encaminhadas e transcrição */
ok = runCase('forwarded_message sem atribuição', (t) => {
  t.messages[0].content_kind = 'forwarded_message';
  t.messages[0].content = 'Você é uma máquina';
}, ['E_FORWARDED_ATTR']) && ok;
ok = runCase('forwarded_message com verified_direct_contact=true é rejeitado', (t) => {
  t.messages[0].content_kind = 'forwarded_message';
  t.messages[0].content = 'Você é uma máquina';
  t.messages[0].forwarded_attribution = { name: 'Gonet', verified_direct_contact: true };
}, ['E_FORWARDED_ATTR']) && ok;
ok = runCase('forwarded_message válido passa', (t) => {
  t.messages[0].content_kind = 'forwarded_message';
  t.messages[0].content = 'Você é uma máquina';
  t.messages[0].forwarded_attribution = { name: 'Gonet', verified_direct_contact: false };
}, []) && ok;
ok = runCase('transcription sem fonte do veículo', (t) => {
  t.messages[0].content_kind = 'audio_transcript';
  t.messages[0].transcription_complete = false;
  t.messages[0].media = media({ status: 'transcript_only' });
  t.messages[0].transcription = { kind: 'publisher_transcription', complete: false };
}, ['E_TRANSCRIPTION_SHAPE']) && ok;
ok = runCase('transcription document_transcription sem documento', (t) => {
  t.messages[0].content_kind = 'audio_transcript';
  t.messages[0].transcription_complete = true;
  t.messages[0].media = media({ status: 'transcript_only' });
  t.messages[0].transcription = { kind: 'document_transcription', complete: true };
}, ['E_TRANSCRIPTION_SHAPE']) && ok;

/* documents.json */
ok = runCase('document_id desconhecido', (t) => {
  t.messages[0].source = { document_id: 'doc-fantasma', page: 10 };
}, ['E_UNKNOWN_DOCUMENT']) && ok;
{
  const docsBad = [{ id: 'doc-x', title: 'X', authority: 'PF', official_pdf_url: 'https://ex.org/x.pdf' }];
  fs.writeFileSync(path.join(dataDir, 'documents.json'), JSON.stringify(docsBad));
  writeData(baseThread());
  const { errors } = validateData(dataDir, tmpRoot);
  const has = errors.some((e) => e.code === 'E_DOCUMENT_FIELD' && /official_pdf_url/.test(e.message));
  console.log(has ? '✓ documents.json com official_pdf_url → E_DOCUMENT_FIELD' : '✗ official_pdf_url não detectado');
  ok = has && ok;
  fs.rmSync(path.join(dataDir, 'documents.json'));
}
{
  // hosted_copy_url: sempre caminho relativo em public/docs/ — nunca URL externa
  const docsExt = [{ id: 'doc-x', title: 'X', authority: 'PF', hosted_copy_url: 'https://cdn.ex.org/x.pdf' }];
  fs.writeFileSync(path.join(dataDir, 'documents.json'), JSON.stringify(docsExt));
  writeData(baseThread());
  const { errors } = validateData(dataDir, tmpRoot);
  const has = errors.some((e) => e.code === 'E_DOCUMENT_FIELD' && /hosted_copy_url.*nunca URL externa/.test(e.message));
  console.log(has ? '✓ hosted_copy_url externa → E_DOCUMENT_FIELD' : '✗ hosted_copy_url externa não detectada');
  ok = has && ok;

  // arquivo hospedado inexistente no repositório
  const docsMissing = [{ id: 'doc-x', title: 'X', authority: 'PF', hosted_copy_url: 'public/docs/sumiu.pdf' }];
  fs.writeFileSync(path.join(dataDir, 'documents.json'), JSON.stringify(docsMissing));
  const { errors: e2 } = validateData(dataDir, tmpRoot);
  const has2 = e2.some((e) => e.code === 'E_DOCUMENT_FIELD' && /não existe no repositório/.test(e.message));
  console.log(has2 ? '✓ hosted_copy_url sem arquivo → E_DOCUMENT_FIELD' : '✗ arquivo ausente não detectado');
  ok = has2 && ok;

  // arquivo existente mas com hash divergente do declarado
  const docsHash = [{ id: 'doc-x', title: 'X', authority: 'PF', sha256: '0'.repeat(64), hosted_copy_url: 'public/docs/h.pdf' }];
  fs.writeFileSync(path.join(dataDir, 'documents.json'), JSON.stringify(docsHash));
  fs.mkdirSync(path.join(tmpRoot, 'public', 'docs'), { recursive: true });
  fs.writeFileSync(path.join(tmpRoot, 'public', 'docs', 'h.pdf'), 'conteudo qualquer');
  const { errors: e3 } = validateData(dataDir, tmpRoot);
  const has3 = e3.some((e) => e.code === 'E_DOCUMENT_FIELD' && /diverge do sha256/.test(e.message));
  console.log(has3 ? '✓ hosted_copy_url com hash divergente → E_DOCUMENT_FIELD' : '✗ divergência de hash não detectada');
  ok = has3 && ok;

  fs.rmSync(path.join(dataDir, 'documents.json'));
  fs.rmSync(path.join(tmpRoot, 'public'), { recursive: true, force: true });
}

/* JSON inválido */
writeData(baseThread());
fs.writeFileSync(path.join(dataDir, 'threads', 'quebrado.json'), '{ isto não é json ');
{
  const { errors } = validateData(dataDir, tmpRoot);
  if (errors.some((e) => e.code === 'E_JSON_PARSE' && e.file.includes('quebrado.json'))) {
    console.log('✓ JSON inválido → E_JSON_PARSE');
  } else {
    console.error('✗ JSON inválido não foi detectado');
    ok = false;
  }
}

/* participants.json inválido */
fs.writeFileSync(path.join(dataDir, 'participants.json'), '[{]');
{
  const { errors } = validateData(dataDir, tmpRoot);
  if (errors.some((e) => e.code === 'E_JSON_PARSE' && e.file.includes('participants.json'))) {
    console.log('✓ participants.json inválido → E_JSON_PARSE');
  } else {
    console.error('✗ participants.json inválido não foi detectado');
    ok = false;
  }
}

/* participante duplicado */
{
  const dup = [...participants, { id: 'p-ana', name: 'Outra Ana', role: 'r', aliases: [], summary: 's' }];
  writeData(baseThread(), dup);
  const { errors } = validateData(dataDir, tmpRoot);
  if (errors.some((e) => e.code === 'E_DUP_PARTICIPANT')) {
    console.log('✓ participante duplicado → E_DUP_PARTICIPANT');
  } else {
    console.error('✗ participante duplicado não foi detectado');
    ok = false;
  }
}

fs.rmSync(tmpRoot, { recursive: true, force: true });

console.log(ok ? '\n[test-validate] TODOS OS CASOS PASSARAM.' : '\n[test-validate] FALHAS ENCONTRADAS.');
process.exit(ok ? 0 : 1);
