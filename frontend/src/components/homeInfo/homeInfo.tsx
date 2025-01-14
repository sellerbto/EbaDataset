import React from 'react';
import './homeInfo.scss';

const HomeInfo: React.FC = () => {
    return (
        <div className='home-info-container'>
            <div className='home-info-content'>
                <h1 className='title'>Удаленная система контроля датасетов</h1>
                <p className='paragraph'>
                    Добро пожаловать в наш инструмент для агрегации информации о
                    распределённых датасетах в среде Linux-серверов.
                </p>
                <p className='paragraph'>
                    Каждый сервер запускает специальный клиент, который собирает
                    данные о локальных датасетах и отправляет их на мастер-ноду.
                    Мастер-нода аккумулирует всю полученную информацию и
                    предоставляет централизованный обзор состояния датасетов.
                </p>
                <p className='paragraph'>
                    Наш фронтенд визуализирует собранные данные, чтобы у
                    специалиста, например ML-инженера, на дополнительном
                    мониторе всегда был актуальный обзор. Если датасет был
                    обновлён, вы сразу это заметите.
                </p>
                <div className='features-list'>
                    <div className='feature'>
                        <span className='feature-icon'>🔧</span>
                        <div>
                            <h3 className='feature-title'>Агрегация данных</h3>
                            <p className='feature-text'>
                                Автоматический сбор и объединение информации о
                                датасетах со всех подключённых серверов.
                            </p>
                        </div>
                    </div>
                    <div className='feature'>
                        <span className='feature-icon'>📊</span>
                        <div>
                            <h3 className='feature-title'>
                                Наглядная визуализация
                            </h3>
                            <p className='feature-text'>
                                Удобные таблицы и графики, чтобы быстро понять
                                текущее состояние и изменения.
                            </p>
                        </div>
                    </div>
                    <div className='feature'>
                        <span className='feature-icon'>⏱</span>
                        <div>
                            <h3 className='feature-title'>Актуальность</h3>
                            <p className='feature-text'>
                                Постоянное обновление данных в реальном времени,
                                чтобы вы не пропустили важные изменения.
                            </p>
                        </div>
                    </div>
                </div>
                <p className='final-note'>
                    Используйте этот инструмент, чтобы всегда быть в курсе
                    актуальной информации о ваших распределённых датасетах и
                    быстрее принимать решения.
                </p>
            </div>
        </div>
    );
};

export default HomeInfo;
