import { Entity, PrimaryGeneratedColumn, Column, PrimaryColumn } from 'typeorm';
import { IsOptional, IsString, IsNumber, IsDate, Length, IsIn, IsEmail } from 'class-validator';

@Entity({ name: 'BLINK_USER_REQUEST' })
export class LOCAL_USER_REQUEST {
  @PrimaryColumn({ type: 'varchar', length: 30 })
  @IsString()
  @Length(0, 30)
  ID: string = "";

  @Column({ name: 'CREATED_BY_USER', nullable: true, default: null, type: 'varchar2', length: 50 })
  @IsOptional()
  @IsString()
  @Length(0, 50)
  CREATED_BY_USER: string = '';

  @Column({ name: 'CREATED_DATETIME', type: 'timestamp', nullable: true, default: () => 'CURRENT_TIMESTAMP' })
  @IsOptional()
  @IsDate()
  CREATED_DATETIME: Date = new Date();

  @Column({ name: 'UPDATED_BY_USER', nullable: true, default: null, type: 'varchar2', length: 50 })
  @IsOptional()
  @IsString()
  @Length(0, 50)
  UPDATED_BY_USER: string = '';

  @Column({ name: 'UPDATED_DATETIME', type: 'timestamp', nullable: true, default: () => 'CURRENT_TIMESTAMP' })
  @IsOptional()
  @IsDate()
  UPDATED_DATETIME: Date = new Date();

  @Column({ name: 'BOOL_SPARE1VAL', type: 'char', length: 1, nullable: true, default: '0' })
  @IsOptional()
  @IsIn(['0', '1'])
  BOOL_SPARE1VAL: '0' | '1' | null = '0';

  @Column({ name: 'BOOL_SPARE2VAL', type: 'char', length: 1, nullable: true, default: '0' })
  @IsOptional()
  @IsIn(['0', '1'])
  BOOL_SPARE2VAL: '0' | '1' | null = '0';

  @Column({ name: 'BOOL_SPARE3VAL', type: 'char', length: 1, nullable: true, default: '0' })
  @IsOptional()
  @IsIn(['0', '1'])
  BOOL_SPARE3VAL: '0' | '1' | null = '0';

  @Column({ name: 'BOOL_SPARE4VAL', type: 'char', length: 1, nullable: true, default: '0' })
  @IsOptional()
  @IsIn(['0', '1'])
  BOOL_SPARE4VAL: '0' | '1' | null = '0';

  @Column({ name: 'BOOL_SPARE5VAL', type: 'char', length: 1, nullable: true, default: '0' })
  @IsOptional()
  @IsIn(['0', '1'])
  BOOL_SPARE5VAL: '0' | '1' | null = '0';

  @Column({ name: 'CREATED_BY', nullable: true, default: null, type: 'varchar2', length: 50 })
  @IsOptional()
  @IsString()
  @Length(0, 50)
  CREATED_BY: string = '';

  @Column({ name: 'DATE_CREATED', type: 'timestamp', nullable: true, default: () => 'CURRENT_TIMESTAMP' })
  @IsOptional()
  @IsDate()
  DATE_CREATED: Date = new Date();

  @Column({ name: 'INT_SPARE1VAL', nullable: false, default: null, type: 'number' })
  @IsNumber()
  INT_SPARE1VAL: number = 0;

  @Column({ name: 'INT_SPARE2VAL', nullable: true, default: null, type: 'number' })
  @IsOptional()
  @IsNumber()
  INT_SPARE2VAL: number = 0;

  @Column({ name: 'INT_SPARE3VAL', nullable: true, default: null, type: 'number' })
  @IsOptional()
  @IsNumber()
  INT_SPARE3VAL: number = 0;

  @Column({ name: 'INT_SPARE4VAL', nullable: true, default: null, type: 'number' })
  @IsOptional()
  @IsNumber()
  INT_SPARE4VAL: number = 0;

  @Column({ name: 'INT_SPARE5VAL', nullable: true, default: null, type: 'number' })
  @IsOptional()
  @IsNumber()
  INT_SPARE5VAL: number = 0;

  @Column({ name: 'IS_ENABLED', type: 'char', length: 1, nullable: true, default: '1' })
  @IsOptional()
  @IsIn(['0', '1'])
  IS_ENABLED: '0' | '1' | null = '1';

  @Column({ name: 'LAST_UPDATED', type: 'timestamp', nullable: true, default: () => 'CURRENT_TIMESTAMP' })
  @IsOptional()
  @IsDate()
  LAST_UPDATED: Date = new Date();

  @Column({ name: 'MODIFIED_BY', nullable: true, default: null, type: 'varchar2', length: 50 })
  @IsOptional()
  @IsString()
  @Length(0, 50)
  MODIFIED_BY: string = '';

  @Column({ name: 'STR_SPARE1VAL', length: 50, type: 'varchar2' })
  @IsOptional()
  @IsString()
  @Length(0, 50)
  STR_SPARE1VAL: string = '';

  @Column({ name: 'STR_SPARE2VAL', length: 50, nullable: true, default: '', type: 'varchar2' })
  @IsOptional()
  @IsString()
  @Length(0, 50)
  STR_SPARE2VAL: string = '';

  @Column({ name: 'STR_SPARE3VAL', length: 50, nullable: true, default: '', type: 'varchar2' })
  @IsOptional()
  @IsString()
  @Length(0, 50)
  STR_SPARE3VAL: string = '';

  @Column({ name: 'STR_SPARE4VAL', length: 50, type: 'varchar2' })
  @IsString()
  @Length(0, 50)
  STR_SPARE4VAL: string = '';

  @Column({ name: 'STR_SPARE5VAL', length: 50, nullable: true, default: '', type: 'varchar2' })
  @IsOptional()
  @IsString()
  @Length(0, 50)
  STR_SPARE5VAL: string = '';

  @Column({ name: 'BACK_END_MODULE', length: 50, nullable: true, default: '', type: 'varchar2' })
  @IsOptional()
  @IsString()
  @Length(0, 50)
  BACK_END_MODULE: string = '';

  @Column({ name: 'MODULE_STATUS', nullable: true, default: null, type: 'number' })
  @IsOptional()
  @IsNumber()
  MODULE_STATUS: number = 0;

  @Column({ name: 'STR_SPARE6VAL', length: 50, nullable: true, default: '', type: 'varchar2' })
  @IsOptional()
  @IsString()
  @Length(0, 50)
  STR_SPARE6VAL: string = '';

  @Column({ name: 'STR_SPARE7VAL', length: 50, nullable: true, default: '', type: 'varchar2' })
  @IsOptional()
  @IsString()
  @Length(0, 50)
  STR_SPARE7VAL: string = '';

  @Column({ name: 'DATE_SPARE1VAL', type: 'date', nullable: true, default: null })
  @IsOptional()
  @IsDate()
  DATE_SPARE1VAL: Date = new Date();

  @Column({ name: 'DATE_SPARE2VAL', type: 'date', nullable: true, default: null })
  @IsOptional()
  @IsDate()
  DATE_SPARE2VAL: Date = new Date();

  @Column({ name: 'DATE_SPARE3VAL', type: 'date', nullable: true, default: null })
  @IsOptional()
  @IsDate()
  DATE_SPARE3VAL: Date = new Date();

  @Column({ name: 'DATE_SPARE4VAL', type: 'date', nullable: true, default: null })
  @IsOptional()
  @IsDate()
  DATE_SPARE4VAL: Date = new Date();

  @Column({ name: 'DATE_SPARE5VAL', type: 'date', nullable: true, default: null })
  @IsOptional()
  @IsDate()
  DATE_SPARE5VAL: Date = new Date();

  @Column({ name: 'STR_SPARE8VAL', length: 50, nullable: true, default: '', type: 'varchar2' })
  @IsOptional()
  @IsString()
  @Length(0, 50)
  STR_SPARE8VAL: string = '';

  @Column({ name: 'STR_SPARE9VAL', length: 50, nullable: true, default: '', type: 'varchar2' })
  @IsOptional()
  @IsString()
  @Length(0, 50)
  STR_SPARE9VAL: string = '';

  @Column({ name: 'STR_SPARE10VAL', length: 50, nullable: true, default: '', type: 'varchar2' })
  @IsOptional()
  @IsString()
  @Length(0, 50)
  STR_SPARE10VAL: string = '';

  @Column({ name: 'ROOM_ID', length: 50, nullable: true, default: '', type: 'varchar2' })
  @IsOptional()
  @IsString()
  @Length(0, 50)
  ROOM_ID: string = '';

  @Column({ name: 'VIDEO_KYC_USER_ID', length: 50, nullable: true, default: '', type: 'varchar2' })
  @IsOptional()
  @IsString()
  @Length(0, 50)
  VIDEO_KYC_USER_ID: string = '';

  @Column({ name: 'VIDEO_KYC_USER_NAME', length: 50, nullable: true, default: '', type: 'varchar2' })
  @IsOptional()
  @IsString()
  @Length(0, 50)
  VIDEO_KYC_USER_NAME: string = '';

  @Column({ name: 'OCR_COMPARISION', type: 'char', length: 1, nullable: true, default: '0' })
  @IsOptional()
  @IsIn(['0', '1'])
  OCR_COMPARISION: '0' | '1' | null = '0';

  @Column({ name: 'ACCOUNT_OPENING_DATE', type: 'date', nullable: true, default: null })
  @IsOptional()
  @IsDate()
  ACCOUNT_OPENING_DATE: Date = new Date();

  @Column({ name: 'PBC_EMAIL', length: 50, nullable: true, default: '', type: 'varchar2' })
  @IsOptional()
  @Length(0, 50)
  PBC_EMAIL: string = '';

  @Column({ name: 'USER_REQUEST', type: 'clob', nullable: true, default: '' })
  @IsOptional()
  @IsString()
  USER_REQUEST: string = '';

  constructor() { }
}
