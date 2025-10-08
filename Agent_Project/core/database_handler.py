from .models import SessionLocal , Profile,ChatMessage 
from .vector_store import index_profile
import json
import ast
from sqlalchemy import or_
import logging
def add_profile_to_db(profile_data:dict,chat_history: json):
    db=SessionLocal()
    try:
        skill_data=profile_data.get('skills')
        if isinstance(skill_data,str):
            try:
                skill_data=ast.literal_eval(skill_data)
                
            except (ValueError,SyntaxError):
                skill_data=[skill_data]
        #chat_history=json.loads(chat_history)
        chat_history=json.dumps(chat_history, ensure_ascii=False)
        skills_as_json_string = json.dumps(skill_data, ensure_ascii=False)
        new_profile=Profile(
            name=profile_data.get("name"),
            field=profile_data.get("field"),
            institution=profile_data.get("institution"),
            years_of_experience=profile_data.get("years_of_experience"),
            skills=skills_as_json_string,
            projects=profile_data.get("projects"),
            interests=profile_data.get("interests"),
            summary=profile_data.get("summary"),
            evaluation=profile_data.get("evaluation"),
            chat_history=chat_history
        )
        db.add(new_profile)
        db.commit()
        db.refresh(new_profile)
        logging.info(f"Profile for '{new_profile.name}' successfully saved to DB.")
        text_to_index = f"Summary: {new_profile.summary}\nEvaluation: {new_profile.evaluation}"
        index_profile(profile_id=new_profile.id, txt_content=text_to_index)
    except Exception as e:    
        print(f"❌ Error saving profile to database: {e}")
        db.rollback()
        return None
    finally:
        db.close()
def search_profiles(filters: dict):
    db=SessionLocal()
    try:
        query=db.query(Profile)
        for key, values in filters.items():
            
            if not isinstance(values, list):
                values = [values]
            if "id" in filters:
                query = query.filter(Profile.id == filters['id'])
            if key == "name":
                query = query.filter(or_(*[Profile.name.ilike(f"%{v}%") for v in values]))
            elif key == "field":
                query = query.filter(or_(*[Profile.field.ilike(f"%{v}%") for v in values]))
            elif key == "institution":
                query = query.filter(or_(*[Profile.institution.ilike(f"%{v}%") for v in values]))
            elif key == "skill":
                query = query.filter(or_(*[Profile.skills.ilike(f'%"{v}"%') for v in values]))
        profiles=query.all()
        if not profiles:
            return f"nothing doesn't found"
        results=[]
        for p in profiles:
            results.append({
                "name": p.name, "field": p.field, "institution": p.institution,
                "skills": json.loads(p.skills) if p.skills else [],
                "summary": p.summary,
                "evaluation":p.evaluation
            })
        return json.dumps(results,ensure_ascii=False,indent=2)
    finally:
        db.close()
def add_chat_message_to_db(session_id: str, role: str, content: str):
    db=SessionLocal()
    try:
        new_message=ChatMessage(
            session_id=session_id,
            role=role,
            content=content
        )
        db.add(new_message)
        db.commit()
    except Exception as e:
        print(f"❌ Error saving chat message: {e}")
        db.rollback()
    finally:
        db.close()