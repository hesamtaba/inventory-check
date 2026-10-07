import re
from dataclasses import dataclass
@dataclass(frozen=True)
class NormalizationSettings:
    uppercase: bool=True; split_dash: bool=True; prefix: str='GD'; min_length: int=3; pattern: str=r'^[A-Z0-9]+$'
def normalize_label(value, s=NormalizationSettings()):
    if value is None: return ''
    v=str(value).strip()
    if s.split_dash: v=re.split(r'\s*[-–—]\s*',v,maxsplit=1)[0].strip()
    if s.uppercase: v=v.upper()
    return v
def canonical_label(value,s=NormalizationSettings()):
    v=normalize_label(value,s)
    p=normalize_label(s.prefix,NormalizationSettings(split_dash=False,prefix='')) if s.prefix else ''
    if p and v and not v.startswith(p): v=p+v
    return v
def is_valid_label(value,s=NormalizationSettings()):
    v=normalize_label(value,s)
    return bool(v) and len(v)>=s.min_length and bool(re.fullmatch(s.pattern,v))
