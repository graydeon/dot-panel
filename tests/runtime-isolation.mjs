// SPDX-License-Identifier: AGPL-3.0-only
import assert from 'node:assert/strict';
import {runtimeFixture,callTool} from './runtime-fixture.mjs';
const {mf,db}=await runtimeFixture();
const state=async(token)=>{
 const response=await mf.dispatchFetch('https://fixture.test/api/state',{headers:{authorization:`Bearer ${token}`,'oai-authenticated-user-id':token==='owner-a'?'synthetic-owner-b':'synthetic-owner-a'}});
 assert.equal(response.status,200);return response.json();
};
const post=async(token,path,body)=>mf.dispatchFetch(`https://fixture.test/api/${path}`,{method:'POST',headers:{authorization:`Bearer ${token}`,'Content-Type':'application/json',origin:'https://fixture.test','oai-authenticated-user-id':'synthetic-owner-a'},body:JSON.stringify(body)});
try {
 for(const [token,name] of [['owner-a','Fixture Alpha'],['owner-b','Fixture Beta']]) {
  const result=await callTool(mf,token,'set_dot_display_name',{dot_display_name:name});assert.equal(result.body.result.isError,false);
 }
 assert.equal((await state('owner-a')).dot_display_name,'Fixture Alpha');
 assert.equal((await state('owner-b')).dot_display_name,'Fixture Beta');
 const configured=await callTool(mf,'owner-a','update_panel_config',{expected_version:0,reviewed_with_owner:true,modules:[{id:'fixture-project',title:'Synthetic project',kind:'project',placement:'primary',enabled:true,source_type:'manual',mode:'agent_snapshot',links:[]}]});assert.equal(configured.body.result.isError,false);
 const configA=await callTool(mf,'owner-a','get_panel_config');assert.equal(configA.body.result.structuredContent.initialized,true);
 const configB=await callTool(mf,'owner-b','get_panel_config');assert.equal(configB.body.result.structuredContent.initialized,false);assert.deepEqual(configB.body.result.structuredContent.modules,[]);
 const calendar=await callTool(mf,'owner-a','update_calendar_snapshot',{calendar_name:'Synthetic calendar',timezone:'Etc/UTC',range_start:'2026-09-01',range_end:'2026-10-01',source_synced_at:'2026-09-01T00:00:00Z',expected_synced_at:null,events:[{event_id:'fixture-event',title:'Synthetic event',start:'2026-09-01',end:'2026-09-02',all_day:true}]});assert.equal(calendar.body.result.isError,false);
 for(const [token,expected] of [['owner-a','Synthetic calendar'],['owner-b',null]]) {
  const response=await mf.dispatchFetch('https://fixture.test/api/calendar',{headers:{authorization:`Bearer ${token}`,'oai-authenticated-user-id':'synthetic-owner-a'}});assert.equal(response.status,200);assert.equal((await response.json()).snapshot?.calendar_name??null,expected);
 }
 const usage=await callTool(mf,'owner-a','update_usage_snapshot',{source:'Synthetic fixture',fetched_at:'2026-09-01T00:00:00Z',expected_fetched_at:null,buckets:[],notes:'Fixture only'});assert.equal(usage.body.result.isError,false);
 const otherUsage=await mf.dispatchFetch('https://fixture.test/api/usage',{headers:{authorization:'Bearer owner-b'}});assert.equal((await otherUsage.json()).snapshot,null);
 const layout=await mf.dispatchFetch('https://fixture.test/api/layout',{headers:{authorization:'Bearer owner-b'}});assert.equal(layout.status,200);assert.equal((await layout.json()).widgets.some(widget=>widget.id.includes('fixture-project')),false);
 const created=await callTool(mf,'owner-a','enqueue_touch_question',{request_id:'fixture-owner-a-question',question:'Synthetic owner A preference?',choices:['Alpha','Beta','Gamma']});
 assert.equal(created.body.result.isError,false);
 const question=created.body.result.structuredContent;
 assert.equal((await state('owner-a')).pending_questions.length,1);
 assert.equal((await state('owner-b')).pending_questions.length,0);
 const body={question_id:question.question_id,version:question.version,choice_id:'1',submission_id:'fixture-b-submission'};
 assert.equal((await post('owner-b','answer',body)).status,409,'B cannot answer A question');
 assert.equal((await post('owner-b','cancel',{question_id:question.question_id,expected_version:question.version})).status,409,'B cannot dismiss A question');
 assert.equal((await state('owner-a')).pending_questions.length,1);
 assert.equal((await post('owner-a','answer',{...body,submission_id:'fixture-a-submission'})).status,200);
 const answer=await db.prepare('SELECT event_id FROM answers WHERE owner=?').bind('synthetic-owner-a').first();
 assert.ok(answer?.event_id);
 const readA=await callTool(mf,'owner-a','get_touch_answer',{event_id:answer.event_id});assert.equal(readA.body.result.isError,false);
 for(const name of ['get_touch_answer','acknowledge_touch_answer']) {
  const other=await callTool(mf,'owner-b',name,{event_id:answer.event_id});assert.equal(other.body.error.code,-32602);
 }
 assert.equal((await db.prepare('SELECT acknowledged FROM answers WHERE event_id=?').bind(answer.event_id).first()).acknowledged,null);
 assert.equal((await state('owner-b')).answer,null);
 // An ID is scoped by the trusted owner, so B can independently use the same request ID.
 const other=await callTool(mf,'owner-b','enqueue_touch_question',{request_id:question.question_id,question:'Synthetic owner B preference?',choices:['One','Two','Three']});assert.equal(other.body.result.isError,false);
 assert.equal((await state('owner-b')).pending_questions[0].text,'Synthetic owner B preference?');
 const crossOrigin=await mf.dispatchFetch('https://fixture.test/api/settings',{method:'POST',headers:{authorization:'Bearer owner-a','Content-Type':'application/json',origin:'https://attacker.invalid'},body:JSON.stringify({dot_display_name:'Hijacked'})});assert.equal(crossOrigin.status,409);
 assert.equal((await state('owner-a')).dot_display_name,'Fixture Alpha');
 // Synthetic active subscription seeds only outbox fan-out; no callback/network delivery is made.
 await db.prepare('INSERT INTO subscriptions (id,owner,url,secret,expires) VALUES (?,?,?,?,?)').bind('fixture-sub','synthetic-owner-a','https://callback.invalid/fixture','fixture-not-a-real-secret',new Date(Date.now()+3600000).toISOString()).run();
 const createRace=async(id)=>{
  const result=await callTool(mf,'owner-a','enqueue_touch_question',{request_id:id,question:'Synthetic race preference?',choices:['Yes','No']});
  assert.equal(result.body.result.isError,false);return result.body.result.structuredContent;
 };
 const outcome=async(question)=>{
  const answers=(await db.prepare('SELECT * FROM answers WHERE owner=? AND question_id=?').bind('synthetic-owner-a',question.question_id).all()).results;
  const row=await db.prepare('SELECT status FROM question_queue WHERE owner=? AND id=?').bind('synthetic-owner-a',question.question_id).first();
  const deliveries=(await db.prepare('SELECT d.* FROM deliveries d JOIN answers a ON a.event_id=d.event_id WHERE a.owner=? AND a.question_id=?').bind('synthetic-owner-a',question.question_id).all()).results;
  return {answers,row,deliveries};
 };
 const duplicate=await createRace('fixture-duplicate-race');
 const duplicateInput={question_id:duplicate.question_id,version:duplicate.version,choice_id:'1',submission_id:'fixture-duplicate-submit'};
 const duplicates=await Promise.all(Array.from({length:8},()=>post('owner-a','answer',duplicateInput)));
 assert.ok(duplicates.every(response=>response.status===200),'Identical concurrent retries must succeed idempotently');
 const first=await outcome(duplicate);assert.equal(first.answers.length,1);assert.equal(first.deliveries.length,1);assert.equal(first.answers[0].submission_id,duplicateInput.submission_id);assert.equal(first.deliveries[0].event_id,first.answers[0].event_id);
 const conflict=await post('owner-a','answer',{...duplicateInput,choice_id:'2'});assert.equal(conflict.status,409);assert.equal((await outcome(duplicate)).answers[0].choice_id,'1','Retry cannot overwrite saved choice');
 const opposing=await createRace('fixture-opposing-race');
 const choices=await Promise.all(['1','2'].map(choice_id=>post('owner-a','answer',{question_id:opposing.question_id,version:opposing.version,choice_id,submission_id:`fixture-opposing-submit-${choice_id}`})));
 assert.deepEqual(choices.map(response=>response.status).sort(),[200,409]);
 const winner=await outcome(opposing);assert.equal(winner.answers.length,1);assert.equal(winner.deliveries.length,1);
 const raceWins={answered:0,cancelled:0};
 for(let i=0;i<8;i++) {
  const question=await createRace(`fixture-dismiss-race-${i}`);
  const actions=[()=>post('owner-a','answer',{question_id:question.question_id,version:question.version,choice_id:'1',submission_id:`fixture-race-submit-${i}`}),()=>post('owner-a','cancel',{question_id:question.question_id,expected_version:question.version})];
  if(i%2)actions.reverse();
  const results=await Promise.all(actions.map(action=>action()));
  assert.deepEqual(results.map(response=>response.status).sort(),[200,409],'One answer/dismiss action wins');
  const final=await outcome(question);
  if(final.row.status==='cancelled') {raceWins.cancelled++;assert.equal(final.answers.length,0);assert.equal(final.deliveries.length,0);}
  else {raceWins.answered++;assert.equal(final.row.status,'active');assert.equal(final.answers.length,1);assert.equal(final.deliveries.length,1);}
  const saved=JSON.stringify(final);
  await post('owner-a','answer',{question_id:question.question_id,version:question.version,choice_id:'2',submission_id:`fixture-after-race-${i}`});
  assert.equal(JSON.stringify(await outcome(question)),saved,'Later conflicting choice cannot change winner');
 }
 const dismissed=await createRace('fixture-dismiss-before-answer');
 assert.equal((await post('owner-a','cancel',{question_id:dismissed.question_id,expected_version:dismissed.version})).status,200);
 assert.equal((await post('owner-a','answer',{question_id:dismissed.question_id,version:dismissed.version,choice_id:'1',submission_id:'fixture-after-dismiss'})).status,409);
 const cancelled=await outcome(dismissed);assert.equal(cancelled.row.status,'cancelled');assert.equal(cancelled.answers.length,0);assert.equal(cancelled.deliveries.length,0);
 assert.equal((await post('owner-a','cancel',{question_id:duplicate.question_id,expected_version:duplicate.version})).status,409,'Saved answer survives later dismiss');
 assert.equal((await outcome(duplicate)).answers[0].event_id,first.answers[0].event_id);
 console.log('Observed concurrent race winners (not a claim of every scheduler interleaving):',raceWins);
 // Both writers share one snapshot revision; precisely one may commit the next revision.
 const previous=(await callTool(mf,'owner-a','get_calendar_snapshot')).body.result.structuredContent.snapshot;
 const calendarRace=await Promise.all(['02','03'].map(day=>callTool(mf,'owner-a','update_calendar_snapshot',{calendar_name:`Synthetic writer ${day}`,timezone:'Etc/UTC',range_start:'2026-09-01',range_end:'2026-10-01',source_synced_at:`2026-09-${day}T00:00:00Z`,expected_synced_at:previous.source_synced_at,events:[]})));
 assert.equal(calendarRace.filter(result=>result.body.result?.isError===false).length,1,'Calendar compare-and-swap has one winner');
 const finalCalendar=(await callTool(mf,'owner-a','get_calendar_snapshot')).body.result.structuredContent.snapshot;
 const calendarWinner=calendarRace.find(result=>result.body.result?.isError===false).body.result.structuredContent;
 assert.equal(finalCalendar.source_synced_at,calendarWinner.source_synced_at);
 const usageBefore=(await callTool(mf,'owner-a','get_usage_snapshot')).body.result.structuredContent.snapshot;
 const usageRace=await Promise.all(['02','03'].map(day=>callTool(mf,'owner-a','update_usage_snapshot',{source:`Synthetic writer ${day}`,fetched_at:`2026-09-${day}T00:00:00Z`,expected_fetched_at:usageBefore.fetched_at,buckets:[],notes:'Concurrent fixture'})));
 assert.equal(usageRace.filter(result=>result.body.result?.isError===false).length,1,'Usage compare-and-swap has one winner');
 const finalUsage=(await callTool(mf,'owner-a','get_usage_snapshot')).body.result.structuredContent.snapshot;
 assert.equal(finalUsage.fetched_at,usageRace.find(result=>result.body.result?.isError===false).body.result.structuredContent.fetched_at);
 // Graduation workload: 100 distinct questions, at most four concurrently pending.
 // This exercises local transaction/outbox correctness, not real callback delivery latency.
 const workload={transactions:0,duplicate:0,conflict:0,answerDismiss:0,answered:0,cancelled:0,answerRows:0,outboxRows:0};
 const transaction=async(index)=>{
  const question=await createRace(`fixture-load-question-${index}`);
  const answer=choice_id=>post('owner-a','answer',{question_id:question.question_id,version:question.version,choice_id,submission_id:`fixture-load-submit-${index}-${choice_id}`});
  const dismiss=()=>post('owner-a','cancel',{question_id:question.question_id,expected_version:question.version});
  const scenario=index%3;
  let responses;
  if(scenario===0) {
   responses=await Promise.all(Array.from({length:4},()=>answer('1')));
   assert.ok(responses.every(response=>response.status===200),'Load: same submission retries are idempotent');workload.duplicate++;
  } else if(scenario===1) {
   responses=await Promise.all([answer('1'),answer('2')]);
   assert.deepEqual(responses.map(response=>response.status).sort(),[200,409],'Load: opposing choices have one winner');workload.conflict++;
  } else {
   const actions=index%2?[dismiss,()=>answer('1')]:[()=>answer('1'),dismiss];
   responses=await Promise.all(actions.map(action=>action()));
   assert.deepEqual(responses.map(response=>response.status).sort(),[200,409],'Load: answer/dismiss has one winner');workload.answerDismiss++;
  }
  const final=await outcome(question);
  assert.ok(final.answers.length<=1,'Load: no duplicate answer/event');
  if(final.row.status==='cancelled') {
   assert.equal(scenario,2);assert.equal(final.answers.length,0);assert.equal(final.deliveries.length,0);workload.cancelled++;
  } else {
   assert.equal(final.row.status,'active');assert.equal(final.answers.length,1);assert.equal(final.deliveries.length,1);assert.equal(final.deliveries[0].event_id,final.answers[0].event_id);assert.equal(final.deliveries[0].subscription_id,'fixture-sub');assert.equal(final.deliveries[0].owner,'synthetic-owner-a');workload.answered++;
  }
  const original=JSON.stringify(final);
  const opposite=final.answers[0]?.choice_id==='2'?'1':'2';
  assert.equal((await answer(opposite)).status,409,'Load: final winner cannot be overwritten');
  assert.equal(JSON.stringify(await outcome(question)),original,'Load: retries preserve final event/outbox/state');
  workload.transactions++;workload.answerRows+=final.answers.length;workload.outboxRows+=final.deliveries.length;
 };
 for(let start=0;start<100;start+=4) await Promise.all(Array.from({length:Math.min(4,100-start)},(_,offset)=>transaction(start+offset)));
 assert.equal(workload.transactions,100);assert.equal(workload.duplicate,34);assert.equal(workload.conflict,33);assert.equal(workload.answerDismiss,33);assert.equal(workload.answered+workload.cancelled,100);assert.equal(workload.answerRows,workload.answered);assert.equal(workload.outboxRows,workload.answered);
 const total=await db.prepare("SELECT count(*) AS n,count(DISTINCT event_id) AS events FROM answers WHERE owner=? AND question_id LIKE 'fixture-load-question-%'").bind('synthetic-owner-a').first();assert.equal(total.n,workload.answered);assert.equal(total.events,workload.answered);
 const outbox=await db.prepare("SELECT count(*) AS n,count(DISTINCT d.event_id) AS events FROM deliveries d JOIN answers a ON a.event_id=d.event_id WHERE a.owner=? AND a.question_id LIKE 'fixture-load-question-%'").bind('synthetic-owner-a').first();assert.equal(outbox.n,workload.answered);assert.equal(outbox.events,workload.answered);
 console.log('100-question synthetic local transaction workload passed (observed scheduler outcomes):',workload);
 console.log('Runtime races passed: eight identical concurrent answers -> one answer/outbox; conflicting answers -> one winner; eight answer/dismiss races -> one terminal outcome without overwrite; calendar/usage revision races -> one winner.');
 console.log('Runtime isolation passed: two synthetic owners, forged-header stripping, names/config/calendar/usage/layout registry/queues/answer lookup/acknowledgement/dismissal isolation, same-ID scoping, and cross-origin write rejection.');
} finally {await mf.dispose();}
